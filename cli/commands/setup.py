import os
from pathlib import Path

import click
import yaml

from cli.common.const.const import GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH, LOCAL_FOLDER
from cli.common.const.parameter_names import *
from cli.common.enums.cloud_providers import CloudProviders
from cli.common.enums.dns_registrars import DnsRegistrars
from cli.common.enums.git_providers import GitProviders
from cli.common.state_store import StateStore
from cli.common.utils.generators import random_string_generator
from cli.services.cloud.aws.aws_manager import AWSManager
from cli.services.cloud.azure.azure_manager import AzureManager
from cli.services.cloud.cloud_provider_manager import CloudProviderManager
from cli.services.dependency_manager import DependencyManager
from cli.services.dns.dns_provider_manager import DNSManager
from cli.services.dns.route53.route53 import Route53Manager
from cli.services.keys.key_manager import KeyManager
from cli.services.tf_wrapper import TfWrapper
from cli.services.vcs.git_provider_manager import GitProviderManager
from cli.services.vcs.github.github_manager import GitHubProviderManager
from cli.services.vcs.template_manager import GitOpsTemplateManager


@click.command()
@click.option('--email', '-e', 'email', help='Email address used for alerts', type=click.STRING)
@click.option('--cloud-provider', '-c', 'cloud_provider', help='Cloud provider type',
              type=click.Choice([e.value for e in CloudProviders], case_sensitive=False))
@click.option('--cloud-profile', '-cp', 'cloud_profile', help='Cloud account profile', default='default',
              type=click.STRING)
@click.option('--cloud-account-key', '-cc', 'cloud_key', help='Cloud account access key', type=click.STRING)
@click.option('--cloud-account-secret', '-cs', 'cloud_secret', help='Cloud account access secret', type=click.STRING)
@click.option('--cloud-region', '-r', 'cloud_region', help='Cloud regions', type=click.STRING)
@click.option('--azure-subscription-id', '-azs', 'azure_subscription_id', help='Azure subscription id',
              type=click.STRING)
@click.option('--cluster-name', '-n', 'cluster_name', help='Cluster name', default='cg-devx-cc', type=click.STRING)
@click.option('--dns-registrar', '-d', 'dns_reg', help='DNS registrar',
              type=click.Choice([e.value for e in DnsRegistrars], case_sensitive=False))
@click.option('--dns-registrar-token', '-dt', 'dns_reg_token', help='DNS registrar token', type=click.STRING)
@click.option('--dns-registrar-key', '-dk', 'dns_reg_key', help='DNS registrar key', type=click.STRING)
@click.option('--dns-registrar-secret', '-ds', 'dns_reg_secret', help='DNS registrar secret', type=click.STRING)
@click.option('--domain-name', '-dn', 'domain', help='Domain-name', type=click.STRING)
@click.option('--git-provider', '-g', 'git_provider', help='Git provider', default=GitProviders.GitHub,
              type=click.Choice([e.value for e in GitProviders], case_sensitive=False))
@click.option('--git-org', '-go', 'git_org', help='Git organization name', type=click.STRING)
@click.option('--git-access-token', '-gt', 'git_token', help='Git access token', type=click.STRING)
@click.option('--gitops-repo-name', '-grn', 'gitops_repo_name', help='GitOps repository name', default='gitops',
              type=click.STRING)
@click.option('--gitops-template-url', '-gtu', 'gitops_template_url', help='GitOps repository template url',
              default=GITOPS_REPOSITORY_URL, type=click.STRING)
@click.option('--gitops-template-branch', '-gtb', 'gitops_template_branch', help='GitOps repository template branch',
              default=GITOPS_REPOSITORY_BRANCH, type=click.STRING)
@click.option('--setup-demo-workload', '-dw', 'install_demo', help='Setup demo workload', default=False,
              flag_value='setup-demo')
@click.option('--config-file', '-f', 'config', help='Load parameters from file', type=click.File(mode='r'))
def setup(
        email: str, cloud_provider: CloudProviders, cloud_profile: str, cloud_key: str, cloud_secret: str,
        cloud_region: str, azure_subscription_id: str, cluster_name: str, dns_reg: DnsRegistrars, dns_reg_token: str,
        dns_reg_key: str, dns_reg_secret: str, domain: str, git_provider: GitProviders, git_org: str, git_token: str,
        gitops_repo_name: str, gitops_template_url: str, gitops_template_branch: str, install_demo: bool,
        config: click.File
):
    """Creates new CG DevX installation."""
    click.echo("Setup CG DevX installation...")

    p: StateStore
    if config is not None:
        try:
            from yaml import CLoader as Loader
            d = yaml.load(config, Loader=Loader)
            # TODO: add validation
            p = StateStore(d)

        except yaml.YAMLError as exception:
            click.echo(exception)
            return
    else:
        # TODO: merge file with param override
        p = StateStore({
            OWNER_EMAIL: email,
            CLOUD_PROVIDER: cloud_provider,
            CLOUD_PROFILE: cloud_profile,
            CLOUD_ACCOUNT_ACCESS_KEY: cloud_key,
            CLOUD_ACCOUNT_ACCESS_SECRET: cloud_secret,
            CLOUD_REGION: cloud_region,
            AZURE_SUBSCRIPTION_ID: azure_subscription_id,
            PRIMARY_CLUSTER_NAME: cluster_name,
            DNS_REGISTRAR: dns_reg,
            DNS_REGISTRAR_ACCESS_TOKEN: dns_reg_token,
            DNS_REGISTRAR_ACCESS_KEY: dns_reg_key,
            DNS_REGISTRAR_ACCESS_SECRET: dns_reg_secret,
            DOMAIN_NAME: domain,
            GIT_PROVIDER: git_provider,
            GIT_ORGANIZATION_NAME: git_org,
            GIT_ACCESS_TOKEN: git_token,
            GITOPS_REPOSITORY_NAME: gitops_repo_name,
            GITOPS_REPOSITORY_TEMPLATE_URL: gitops_template_url,
            GITOPS_REPOSITORY_TEMPLATE_BRANCH: gitops_template_branch,
            DEMO_WORKLOAD: install_demo
        })

    # validate parameters
    p.validate_input_params(validator=setup_param_validator)

    # save checkpoint
    p.save_checkpoint()

    # init proper cloud provider
    if p.cloud_provider == CloudProviders.AWS:
        cm: CloudProviderManager = AWSManager(p.get_input_param(CLOUD_REGION),
                                              p.get_input_param(CLOUD_PROFILE),
                                              p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                              p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))

        # check if cloud native DNS registrar is selected
        if p.dns_registrar == DnsRegistrars.Route53:
            if p.get_input_param(DNS_REGISTRAR_ACCESS_KEY) is None and p.get_input_param(
                    DNS_REGISTRAR_ACCESS_SECRET) is None:
                # initialise with cloud account permissions
                dm: DNSManager = Route53Manager(profile=p.get_input_param(CLOUD_PROFILE),
                                                key=p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                                secret=p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))
            else:
                # initialise with provided key and secret
                dm: DNSManager = Route53Manager(
                    key=p.get_input_param(DNS_REGISTRAR_ACCESS_KEY),
                    secret=p.get_input_param(DNS_REGISTRAR_ACCESS_SECRET))

    elif p.cloud_provider == CloudProviders.Azure:
        cm: AzureManager = AzureManager(p.get_input_param(AZURE_SUBSCRIPTION_ID))

    p.parameters["<CLOUD_REGION>"] = cm.region

    # init proper git provider
    if p.git_provider == GitProviders.GitHub:
        gm: GitProviderManager = GitHubProviderManager(p.get_input_param(GIT_ACCESS_TOKEN),
                                                       p.get_input_param(GIT_ORGANIZATION_NAME))

    # init proper dns registrar provider
    # Note!: Route53 is initialised with AWS Cloud Provider

    if not p.has_checkpoint("preflight"):
        click.echo("Executing pre-flight checks...")

        cloud_provider_check(cm, p)
        click.echo("Cloud provider pre-flight check. Done!")

        git_provider_check(gm, p)
        click.echo("Git provider pre-flight check. Done!")

        git_user_login, git_user_name, git_user_email = gm.get_current_user_info()
        p.internals["GIT_USER_LOGIN"] = git_user_login
        p.internals["GIT_USER_NAME"] = git_user_name
        p.internals["GIT_USER_EMAIL"] = git_user_email
        p.parameters["# <GIT_PROVIDER_MODULE>"] = gm.create_tf_module_snippet()

        dns_provider_check(dm, p)
        click.echo("DNS provider pre-flight check. Done!")

        # create ssh keys
        click.echo("Generating ssh keys...")
        default_public_key, public_key_path, private_key_path = KeyManager.create_ed_keys()
        p.parameters["<VCS_BOT_SSH_PUBLIC_KEY>"] = default_public_key
        p.internals["DEFAULT_SSH_PUBLIC_KEY_PATH"] = public_key_path
        p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"] = private_key_path

        # Optional K8s cluster keys
        k8s_public_key, k8s_public_key_path, k8s_private_key_path = KeyManager.create_rsa_keys()
        p.parameters["<CC_CLUSTER_SSH_PUBLIC_KEY>"] = k8s_public_key
        p.internals["CLUSTER_SSH_PUBLIC_KEY_PATH"] = k8s_public_key_path
        p.internals["CLUSTER_SSH_PRIVATE_KEY_PATH"] = k8s_private_key_path

        click.echo("Generating ssh keys. Done!")

        # create terraform storage backend
        click.echo("Creating tf backend storage...")
        tf_backend_storage_name: str = f'{p.get_input_param(GITOPS_REPOSITORY_NAME)}-{random_string_generator()}'.lower()

        tf_backend_location = cm.create_iac_state_storage(tf_backend_storage_name)

        p.parameters["# <TF_VCS_REMOTE_BACKEND>"] = cm.create_iac_backend_snippet(tf_backend_storage_name, cm.region,
                                                                                  "vcs")
        p.parameters["# <TF_HOSTING_REMOTE_BACKEND>"] = cm.create_iac_backend_snippet(tf_backend_storage_name,
                                                                                      cm.region,
                                                                                      "hosting_provider")
        p.parameters["# <TF_HOSTING_PROVIDER>"] = cm.create_hosting_provider_snippet()

        p.parameters["<K8S_AWS_SERVICE_ACCOUNT_ROLE_MAPPING>"] = cm.create_k8s_rol_binding_snippet()

        click.echo("Creating tf backend storage. Done!")

        p.set_checkpoint("preflight")
        p.save_checkpoint()
        click.echo("Pre-flight checks. Done!")

    # end preflight check section
    else:
        click.echo("Skipped pre-flight checks.")

    dm: DependencyManager = DependencyManager()

    if not p.has_checkpoint("dependencies"):
        click.echo("Dependencies check...")

        # terraform
        if dm.check_tf():
            click.echo("tf is installed. Continuing...")
        else:
            click.echo("Downloading and installing tf...")
            dm.install_tf()
            click.echo("tf is installed.")

        # kubectl
        if dm.check_kubectl():
            click.echo("kubectl is installed. Continuing...")
        else:
            click.echo("Downloading and installing kubectl...")
            dm.install_kubectl()
            click.echo("kubectl is installed.")

        click.echo("Dependencies check. Done!")
        p.set_checkpoint("dependencies")
        p.save_checkpoint()
    else:
        click.echo("Skipped dependencies check.")

    # promote input params
    # TODO: move to appropriate place
    p.parameters["<OWNER_EMAIL>"] = p.get_input_param(OWNER_EMAIL)
    p.parameters["<CLOUD_PROVIDER>"] = p.cloud_provider
    p.parameters["<PRIMARY_CLUSTER_NAME>"] = p.get_input_param(PRIMARY_CLUSTER_NAME)
    p.parameters["<GIT_PROVIDER>"] = p.git_provider
    p.parameters["<GITOPS_REPOSITORY_NAME>"] = p.get_input_param(GITOPS_REPOSITORY_NAME)
    p.parameters["<GIT_ORGANIZATION_NAME>"] = p.get_input_param(GIT_ORGANIZATION_NAME)
    p.parameters["<DOMAIN_NAME>"] = p.get_input_param(DOMAIN_NAME)
    p.parameters["<GIT_REPOSITORY_ROOT>"] = f'github.com/{p.get_input_param(GIT_ORGANIZATION_NAME)}/*'

    p.parameters["<ATLANTIS_WEBHOOK_SECRET>"] = random_string_generator(20)

    # Ingress URLs for core components. Note!: URL does not contain protocol
    cluster_fqdn = f'{p.get_input_param(PRIMARY_CLUSTER_NAME)}.{p.get_input_param(DOMAIN_NAME)}'
    p.parameters["<CC_CLUSTER_FQDN>"] = cluster_fqdn
    p.parameters["<VAULT_INGRESS_URL>"] = f'vault.{cluster_fqdn}'
    p.parameters["<ARGO_CD_INGRESS_URL>"] = f'argocd.{cluster_fqdn}'
    p.parameters["<ARGO_WORKFLOW_INGRESS_URL>"] = f'argo.{cluster_fqdn}'
    p.parameters["<ATLANTIS_INGRESS_URL>"] = f'atlantis.{cluster_fqdn}'
    p.parameters["<HARBOR_INGRESS_URL>"] = f'harbor.{cluster_fqdn}'
    p.parameters["<GRAFANA_INGRESS_URL>"] = f'grafana.{cluster_fqdn}'
    p.parameters["<SONARQUBE_INGRESS_URL>"] = f'sonarqube.{cluster_fqdn}'

    # OIDC config
    vault_i = p.parameters["<VAULT_INGRESS_URL>"]
    p.parameters["<OIDC_PROVIDER_URL>"] = f'{vault_i}/v1/identity/oidc/provider/cgdevx'
    p.parameters["<OIDC_PROVIDER_AUTHORIZE_URL>"] = f'{vault_i}/ui/vault/identity/oidc/provider/cgdevx/authorize'
    p.parameters["<OIDC_PROVIDER_TOKEN_URL>"] = f'{vault_i}/v1/identity/oidc/provider/cgdevx/token'
    p.parameters["<OIDC_PROVIDER_USERINFO_URL>"] = f'{vault_i}/v1/identity/oidc/provider/cgdevx/userinfo'

    p.parameters["<ARGO_CD_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<ARGO_CD_INGRESS_URL>"]}/oauth2/callback'
    p.parameters["<HARBOR_REGISTRY_URL>"] = f'{p.parameters["<HARBOR_INGRESS_URL>"]}'

    p.save_checkpoint()

    # params section end

    tm = GitOpsTemplateManager(p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_URL),
                               p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_BRANCH),
                               p.get_input_param(GIT_ACCESS_TOKEN))

    if not p.has_checkpoint("repo-prep"):
        click.echo("Preparing your GitOps code...")

        tm.check_repository_existence()
        tm.clone()
        tm.restructure_template()
        tm.parametrise_tf(p.parameters)

        p.set_checkpoint("repo-prep")
        p.save_checkpoint()

        click.echo("Preparing your GitOps code. Done!")
    else:
        click.echo("Skipped GitOps code prep.")

    click.echo("Provisioning VCS...")
    # use to enable tf debug
    # "TF_LOG": "DEBUG", "TF_LOG_PATH": "/Users/a1m/.cgdevx/gitops/terraform/vcs/terraform.log",
    # drop empty values
    tf_env_vars = {k: v for k, v in {
        "AWS_PROFILE": p.get_input_param(CLOUD_PROFILE),
        "AWS_ACCESS_KEY_ID": p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
        "AWS_SECRET_ACCESS_KEY": p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET),
        "AWS_DEFAULT_REGION": p.parameters["<CLOUD_REGION>"],
    }.items() if v}
    tf_folder = Path().home() / LOCAL_FOLDER / "gitops" / "terraform"

    # VCS section
    if not p.has_checkpoint("vcs-tf"):
        # vcs env vars
        vcs_tf_env_vars = tf_env_vars | {"GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
                                         "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME)}

        # set envs as required by tf
        for k, vault_i in vcs_tf_env_vars.items():
            os.environ[k] = vault_i

        tf_wrapper = TfWrapper(tf_folder / "vcs")
        tf_wrapper.init()
        tf_wrapper.apply({"atlantis_repo_webhook_secret": p.parameters["<ATLANTIS_WEBHOOK_SECRET>"],
                          "vcs_bot_ssh_public_key": p.parameters["<VCS_BOT_SSH_PUBLIC_KEY>"]})
        vcs_out = tf_wrapper.output()

        # store out params
        p.parameters["<GIT_REPOSITORY_GIT_URL>"] = vcs_out["gitops_repo_ssh_clone_url"]

        # unset envs as no longer needed
        for k in vcs_tf_env_vars.keys():
            os.environ.pop(k)

        p.set_checkpoint("vcs-tf")
        p.save_checkpoint()

        click.echo("Provisioning VCS. Done!")
    else:
        click.echo("Skipped VCS provisioning.")

    # K8s Cluster section
    if not p.has_checkpoint("k8s-tf"):
        click.echo("Provisioning K8s cluster...")

        # run hosting provider tf to create K8s cluster
        hp_tf_env_vars = {
            **{},  # add vars here
            **tf_env_vars}
        # set envs as required by tf
        for k, vault_i in hp_tf_env_vars.items():
            os.environ[k] = vault_i

        tf_wrapper = TfWrapper(tf_folder / "hosting_provider")
        tf_wrapper.init()
        tf_wrapper.apply()
        hp_out = tf_wrapper.output()

        # store out params
        # network
        p.parameters["<NETWORK_ID>"] = hp_out["network_id"]
        # roles
        p.parameters["<ARGO_WORKFLOW_IAM_ROLE_RN>"] = hp_out["iam_argoworkflow_role"]
        p.parameters["<ARGO_CD_IAM_ROLE_RN>"] = hp_out["iam_argoworkflow_role"]  # TODO: use own role
        p.parameters["<ATLANTIS_IAM_ROLE_RN>"] = hp_out["atlantis_role"]
        p.parameters["<CERT_MANAGER_IAM_ROLE_RN>"] = hp_out["cert_manager_role"]
        p.parameters["<HARBOR_IAM_ROLE_RN>"] = hp_out["harbor_role"]
        p.parameters["<EXTERNAL_DNS_IAM_ROLE_RN>"] = hp_out["external_dns_role"]
        p.parameters["<VAULT_IAM_ROLE_RN>"] = hp_out["vault_role"]
        # cluster
        p.parameters["<CC_CLUSTER_ENDPOINT>"] = hp_out["cluster_endpoint"]
        p.parameters["<CC_CLUSTER_OIDC_PROVIDER>"] = hp_out["cluster_oidc_provider"]  # do we need it?

        # unset envs as no longer needed
        for k in hp_tf_env_vars.keys():
            os.environ.pop(k)

        p.set_checkpoint("k8s-tf")
        p.save_checkpoint()

        click.echo("Provisioning K8s cluster. Done!")
    else:
        click.echo("Skipped VCS provisioning.")

    if not p.has_checkpoint("gitops-vcs"):
        tm.parametrise_registry(p.parameters)
        tm.parametrise_root(p.parameters)

        click.echo("Pushing GitOps code...")

        tm.upload(p.parameters["<GIT_REPOSITORY_GIT_URL>"],
                  p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
                  p.internals["GIT_USER_NAME"],
                  p.internals["GIT_USER_EMAIL"])

        click.echo("Pushing GitOps code. Done!")

        p.set_checkpoint("gitops-vcs")
        p.save_checkpoint()
    else:
        click.echo("Skipped GitOps repo initialization.")

    # user could get kubeconfig by running command
    # `aws eks update-kubeconfig --region region-code --name my-cluster --kubeconfig my-config-path`
    # CLI could not follow this approach as aws client could be not configured properly when keys are used
    # CLI is creating this file programmatically

    return True


def cloud_provider_check(manager: AzureManager | AWSManager, p: StateStore) -> None:
    if not manager.detect_cli_presence():
        click.ClickException("Cloud CLI is missing")
    if not manager.evaluate_permissions():
        click.ClickException("Insufficient IAM permission")


def git_provider_check(manager: GitProviderManager, p: StateStore) -> None:
    if not manager.evaluate_permissions():
        click.ClickException("Insufficient Git token permissions")
    if manager.check_repository_existence(p.get_input_param(GITOPS_REPOSITORY_NAME)):
        click.ClickException("GitOps repo already exists")


def dns_provider_check(manager: DNSManager, p: StateStore) -> None:
    if not manager.evaluate_permissions():
        click.ClickException("Insufficient DNS permissions")
    if not manager.evaluate_domain_ownership(p.get_input_param(DOMAIN_NAME)):
        click.ClickException("Could not verify domain ownership")


def setup_param_validator(params: StateStore) -> bool:
    if params.dns_registrar is None:
        if params.cloud_provider == CloudProviders.AWS:
            params.dns_registrar = DnsRegistrars.Route53
        if params.cloud_provider == CloudProviders.Azure:
            params.dns_registrar = DnsRegistrars.AzureDNS

    # TODO: validate parameters
    if ((params.get_input_param(CLOUD_PROFILE) is None
         or params.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY) is not None
         or params.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET) is not None)
            and
            (params.get_input_param(CLOUD_PROFILE) is not None
             or params.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY) is None
             or params.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET) is None)):
        click.echo("Cloud account keys validation error: should specify only one of profile or key + secret")
        return False

    return True
