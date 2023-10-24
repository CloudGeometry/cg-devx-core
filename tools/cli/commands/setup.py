import base64
import json
import os
import re
import time

import click
import portforward
import yaml

from common.command_utils import init_cloud_provider
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, \
    LOCAL_TF_FOLDER_SECRETS_MANAGER, LOCAL_TF_FOLDER_USERS
from common.const.const import GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH, KUBECTL_VERSION, FALLBACK_AUTHOR_EMAIL
from common.const.namespaces import ARGOCD_NAMESPACE, ARGO_WORKFLOW_NAMESPACE, EXTERNAL_SECRETS_OPERATOR_NAMESPACE, \
    ATLANTIS_NAMESPACE, VAULT_NAMESPACE
from common.const.parameter_names import CLOUD_PROFILE, OWNER_EMAIL, CLOUD_PROVIDER, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, CLOUD_REGION, PRIMARY_CLUSTER_NAME, DNS_REGISTRAR, DNS_REGISTRAR_ACCESS_TOKEN, \
    DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET, DOMAIN_NAME, GIT_PROVIDER, GIT_ORGANIZATION_NAME, \
    GIT_ACCESS_TOKEN, GITOPS_REPOSITORY_NAME, GITOPS_REPOSITORY_TEMPLATE_URL, GITOPS_REPOSITORY_TEMPLATE_BRANCH, \
    DEMO_WORKLOAD
from common.enums.cloud_providers import CloudProviders
from common.enums.dns_registrars import DnsRegistrars
from common.enums.git_providers import GitProviders
from common.state_store import StateStore
from common.utils.generators import random_string_generator
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.dependency_manager import DependencyManager
from services.dns.dns_provider_manager import DNSManager
from services.k8s.config_builder import create_k8s_config
from services.k8s.delivery_service_manager import DeliveryServiceManager, get_argocd_token
from services.k8s.k8s import KubeClient, write_ca_cert
from services.k8s.kctl_wrapper import KctlWrapper
from services.keys.key_manager import KeyManager
from services.template_manager import GitOpsTemplateManager
from services.tf_wrapper import TfWrapper
from services.vcs.git_provider_manager import GitProviderManager
from services.vcs.github.github_manager import GitHubProviderManager
from services.vcs.gitlab.gitlab_manager import GitLabProviderManager


@click.command()
@click.option('--email', '-e', 'email', help='Email address used for alerts', type=click.STRING)
@click.option('--cloud-provider', '-c', 'cloud_provider', help='Cloud provider type',
              type=click.Choice([e.value for e in CloudProviders], case_sensitive=False))
@click.option('--cloud-profile', '-cp', 'cloud_profile', help='Cloud account profile', default='default',
              type=click.STRING)
@click.option('--cloud-account-key', '-cc', 'cloud_key', help='Cloud account access key', type=click.STRING)
@click.option('--cloud-account-secret', '-cs', 'cloud_secret', help='Cloud account access secret', type=click.STRING)
@click.option('--cloud-region', '-r', 'cloud_region', help='Cloud regions', type=click.STRING)
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
        cloud_region: str, cluster_name: str, dns_reg: DnsRegistrars, dns_reg_token: str,
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

        except yaml.YAMLError as e:
            raise click.ClickException(e)
    else:
        # TODO: merge file with param override
        p = StateStore({
            OWNER_EMAIL: email,
            CLOUD_PROVIDER: cloud_provider,
            CLOUD_PROFILE: cloud_profile,
            CLOUD_ACCOUNT_ACCESS_KEY: cloud_key,
            CLOUD_ACCOUNT_ACCESS_SECRET: cloud_secret,
            CLOUD_REGION: cloud_region,
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

    cloud_man, dns_man = init_cloud_provider(p)

    p.parameters["<CLOUD_REGION>"] = cloud_man.region

    # init proper git provider
    if p.git_provider == GitProviders.GitHub:
        gm: GitProviderManager = GitHubProviderManager(p.get_input_param(GIT_ACCESS_TOKEN),
                                                       p.get_input_param(GIT_ORGANIZATION_NAME))
    elif p.git_provider == GitProviders.GitLab:
        gm: GitProviderManager = GitLabProviderManager(
            p.get_input_param(GIT_ACCESS_TOKEN),
            p.get_input_param(GIT_ORGANIZATION_NAME)
        )
    else:
        click.echo('Error: None of the available Git providers were specified')
        return

    # init proper dns registrar provider
    # Note!: Route53 is initialised with AWS Cloud Provider
    # TODO: DNS provider init

    if not p.has_checkpoint("preflight"):
        click.echo("Executing pre-flight checks...")

        # cloud_provider_check(cloud_man, p)
        click.echo("Cloud provider pre-flight check. Done!")

        # git_provider_check(gm, p)
        click.echo("Git provider pre-flight check. Done!")

        git_user_login, git_user_name, git_user_email = gm.get_current_user_info()
        p.internals["GIT_USER_LOGIN"] = git_user_login
        p.internals["GIT_USER_NAME"] = git_user_name
        p.parameters["<GIT_USER_NAME>"] = git_user_name
        p.internals["GIT_USER_EMAIL"] = git_user_email
        p.parameters["# <GIT_PROVIDER_MODULE>"] = gm.create_tf_module_snippet()

        # dns_provider_check(dns_man, p)
        click.echo("DNS provider pre-flight check. Done!")

        p.set_checkpoint("preflight")
        p.save_checkpoint()
        click.echo("Pre-flight checks. Done!")

    # end preflight check section
    else:
        click.echo("Skipped pre-flight checks.")

    dep_man: DependencyManager = DependencyManager()

    if not p.has_checkpoint("dependencies"):
        click.echo("Dependencies check...")

        # terraform
        if dep_man.check_tf():
            click.echo("tf is installed. Continuing...")
        else:
            click.echo("Downloading and installing tf...")
            dep_man.install_tf()
            click.echo("tf is installed.")

        # kubectl
        if dep_man.check_kubectl():
            click.echo("kubectl is installed. Continuing...")
        else:
            click.echo("Downloading and installing kubectl...")
            dep_man.install_kubectl()
            click.echo("kubectl is installed.")

        click.echo("Dependencies check. Done!")
        p.set_checkpoint("dependencies")
        p.save_checkpoint()
    else:
        click.echo("Skipped dependencies check.")

    if not p.has_checkpoint("one-time-setup"):
        click.echo("Setting initial parameters...")

        # create ssh keys
        click.echo("Generating ssh keys...")
        default_public_key, public_key_path, default_private_key, private_key_path = KeyManager.create_ed_keys()
        p.internals["DEFAULT_SSH_PUBLIC_KEY"] = p.parameters["<VCS_BOT_SSH_PUBLIC_KEY>"] = default_public_key
        p.internals["DEFAULT_SSH_PUBLIC_KEY_PATH"] = public_key_path
        p.internals["DEFAULT_SSH_PRIVATE_KEY"] = default_private_key
        p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"] = private_key_path

        # Optional K8s cluster keys
        k8s_public_key, k8s_public_key_path, k8s_private_key, k8s_private_key_path = KeyManager.create_rsa_keys(
            "cgdevx_k8s_rsa")
        p.parameters["<CC_CLUSTER_SSH_PUBLIC_KEY>"] = k8s_public_key
        p.internals["CLUSTER_SSH_PUBLIC_KEY_PATH"] = k8s_public_key_path
        p.internals["CLUSTER_SSH_PRIVATE_KEY"] = k8s_private_key
        p.internals["CLUSTER_SSH_PRIVATE_KEY_PATH"] = k8s_private_key_path

        click.echo("Generating ssh keys. Done!")

        # create terraform storage backend
        click.echo("Creating tf backend storage...")

        tf_backend_storage = cloud_man.create_iac_state_storage(p.get_input_param(GITOPS_REPOSITORY_NAME))
        p.internals["TF_BACKEND_STORAGE_NAME"] = tf_backend_storage

        p.parameters["# <TF_VCS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                         "vcs")
        p.parameters["# <TF_HOSTING_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                             "hosting_provider")
        p.parameters["# <TF_SECRETS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                             "secrets")
        p.parameters["# <TF_USERS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                           "users")

        p.parameters["# <TF_HOSTING_PROVIDER>"] = cloud_man.create_hosting_provider_snippet()

        p.parameters["<K8S_ROLE_MAPPING>"] = cloud_man.create_k8s_cluster_role_mapping_snippet()

        click.echo("Creating tf backend storage. Done!")

        p.set_checkpoint("one-time-setup")
        p.save_checkpoint()
        click.echo("Setting initial parameters. Done!")

    # end preflight check section
    else:
        click.echo("Skipped setting initial parameters.")

    # promote input params
    prepare_parameters(p)
    p.save_checkpoint()

    tm = GitOpsTemplateManager(p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_URL),
                               p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_BRANCH),
                               p.get_input_param(GIT_ACCESS_TOKEN))

    if not p.has_checkpoint("repo-prep"):
        click.echo("Preparing your GitOps code...")

        tm.check_repository_existence()
        tm.clone()
        tm.build_repo_from_template()
        tm.parametrise_tf(p.parameters)

        p.set_checkpoint("repo-prep")
        p.save_checkpoint()

        click.echo("Preparing your GitOps code. Done!")
    else:
        click.echo("Skipped GitOps code prep.")

    # VCS provisioning

    # use to enable tf debug
    # "TF_LOG": "DEBUG", "TF_LOG_PATH": "/Users/a1m/.cgdevx/gitops/terraform/vcs/terraform.log",
    # drop empty values
    # TODO: cloud provider specific, should add Azure version
    if p.cloud_provider == CloudProviders.AWS:
        cloud_provider_auth_env_vars = {k: v for k, v in {
            "AWS_PROFILE": p.get_input_param(CLOUD_PROFILE),
            "AWS_ACCESS_KEY_ID": p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
            "AWS_SECRET_ACCESS_KEY": p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET),
            "AWS_REGION": p.parameters["<CLOUD_REGION>"],
            "AWS_DEFAULT_REGION": p.parameters["<CLOUD_REGION>"],
        }.items() if v}
    elif p.cloud_provider == CloudProviders.Azure:
        cloud_provider_auth_env_vars = {}
    else:
        cloud_provider_auth_env_vars = {}

    # VCS section
    if not p.has_checkpoint("vcs-tf"):
        click.echo("Provisioning VCS...")
        # vcs env vars
        vcs_tf_env_vars = {
            **cloud_provider_auth_env_vars,
            **{"GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
               "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME)}
        }

        # set envs as required by tf
        set_envs(vcs_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.apply({"atlantis_repo_webhook_secret": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"],
                          "vcs_bot_ssh_public_key": p.parameters["<VCS_BOT_SSH_PUBLIC_KEY>"]})
        vcs_out = tf_wrapper.output()

        # store out params
        p.parameters["<GIT_REPOSITORY_GIT_URL>"] = vcs_out["gitops_repo_ssh_clone_url"]
        p.parameters["<GIT_REPOSITORY_URL>"] = vcs_out["gitops_repo_html_url"]

        # unset envs as no longer needed
        unset_envs(vcs_tf_env_vars)

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
            **cloud_provider_auth_env_vars}
        # set envs as required by tf
        set_envs(hp_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_HOSTING_PROVIDER)
        tf_wrapper.init()
        tf_wrapper.apply({"ssh_public_key": p.parameters["<CC_CLUSTER_SSH_PUBLIC_KEY>"]})
        hp_out = tf_wrapper.output()

        # store out params
        # network
        p.parameters["<NETWORK_ID>"] = hp_out["network_id"]
        # roles
        p.parameters["<CD_IAM_ROLE_RN>"] = hp_out["iam_cd_role"]
        p.parameters["<CI_IAM_ROLE_RN>"] = hp_out["iam_ci_role"]
        p.parameters["<IAC_PR_AUTOMATION_IAM_ROLE_RN>"] = hp_out["iac_pr_automation_role"]
        p.parameters["<CERT_MANAGER_IAM_ROLE_RN>"] = hp_out["cert_manager_role"]
        p.parameters["<REGISTRY_IAM_ROLE_RN>"] = hp_out["registry_role"]
        p.parameters["<EXTERNAL_DNS_IAM_ROLE_RN>"] = hp_out["external_dns_role"]
        p.parameters["<SECRET_MANAGER_IAM_ROLE_RN>"] = hp_out["secret_manager_role"]
        # cluster
        p.internals["CC_CLUSTER_ENDPOINT"] = hp_out["cluster_endpoint"]
        p.internals["CC_CLUSTER_CA_CERT_DATA"] = hp_out["cluster_certificate_authority_data"]
        p.internals["CC_CLUSTER_CA_CERT_PATH"] = write_ca_cert(hp_out["cluster_certificate_authority_data"])
        p.internals["CC_CLUSTER_OIDC_PROVIDER"] = hp_out["cluster_oidc_provider"]  # do we need it?
        # artifact storage
        p.parameters["<CLOUD_BINARY_ARTIFACTS_STORE>"] = hp_out["artifact_storage"]
        # kms keys
        sec_man_key = hp_out["secret_manager_seal_key"]
        p.parameters["<SECRET_MANAGER_SEAL_RN>"] = sec_man_key
        p.parameters["# <SECRET_MANAGER_SEAL>"] = cloud_man.create_secret_manager_seal_snippet(sec_man_key)

        # unset envs as no longer needed
        unset_envs(hp_tf_env_vars)

        # user could get kubeconfig by running command
        # AWS: `aws eks update-kubeconfig --region region-code --name my-cluster --kubeconfig my-config-path`
        # CLI could not follow this approach as aws client could be not configured properly when keys are used
        # CLI is creating this file programmatically
        command, command_args = cloud_man.get_k8s_auth_command()
        kubeconfig_params = {
            "<ENDPOINT>": p.internals["CC_CLUSTER_ENDPOINT"],
            "<CLUSTER_AUTH_BASE64>": p.internals["CC_CLUSTER_CA_CERT_DATA"],
            "<CLUSTER_NAME>": p.parameters["<PRIMARY_CLUSTER_NAME>"],
            "<CLUSTER_REGION>": p.parameters["<CLOUD_REGION>"]
        }
        kctl_config_path = create_k8s_config(command, command_args, cloud_provider_auth_env_vars, kubeconfig_params)
        p.internals["KCTL_CONFIG_PATH"] = kctl_config_path

        p.set_checkpoint("k8s-tf")
        p.save_checkpoint()

        click.echo("Provisioning K8s cluster. Done!")
    else:
        click.echo("Skipped K8s provisioning.")

    if not p.has_checkpoint("gitops-vcs"):
        tm.parametrise_registry(p.parameters)
        tm.parametrise_gitops_readme(p.parameters)

        click.echo("Pushing GitOps code...")

        tm.upload(p.parameters["<GIT_REPOSITORY_GIT_URL>"],
                  p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
                  p.internals["GIT_USER_NAME"],
                  p.internals["GIT_USER_EMAIL"])

        p.set_checkpoint("gitops-vcs")
        p.save_checkpoint()

        click.echo("Pushing GitOps code. Done!")
    else:
        click.echo("Skipped GitOps repo initialization.")

    # k8s
    # default token life-time is 14m
    # to be safe should refresh token each time
    k8s_token = cloud_man.get_k8s_token(p.parameters["<PRIMARY_CLUSTER_NAME>"])
    kube_client = KubeClient(p.internals["CC_CLUSTER_CA_CERT_PATH"], k8s_token, p.internals["CC_CLUSTER_ENDPOINT"])
    kctl = KctlWrapper(p.internals["KCTL_CONFIG_PATH"])
    cd_man = DeliveryServiceManager(kube_client)

    # install ArgoCD
    if not p.has_checkpoint("k8s-delivery"):
        click.echo("Installing ArgoCD...")

        argocd_bootstrap_name = "argocd-bootstrap"
        argocd_core_project_name = "core"

        # get CoreDNS deployments to validate cluster
        coredns_deployment = kube_client.get_deployment("kube-system", "coredns")

        # wait for deployment readiness
        kube_client.wait_for_deployment(coredns_deployment)

        kube_client.create_namespace(ARGOCD_NAMESPACE)
        kube_client.create_service_account(ARGOCD_NAMESPACE, argocd_bootstrap_name)
        kube_client.create_cluster_role(ARGOCD_NAMESPACE, argocd_bootstrap_name)
        # extract role name from arn
        # TODO: move to tf
        argo_cd_role_name = p.parameters["<CD_IAM_ROLE_RN>"].split("/")[-1]
        kube_client.create_cluster_role_binding(ARGOCD_NAMESPACE, argocd_bootstrap_name, argocd_bootstrap_name)

        job = cd_man.create_argocd_bootstrap_job(argocd_bootstrap_name)
        kube_client.wait_for_job(job)
        # cleanup temp resources
        try:
            kube_client.remove_service_account(ARGOCD_NAMESPACE, argocd_bootstrap_name)
            kube_client.remove_cluster_role(argocd_bootstrap_name)
            kube_client.remove_cluster_role_binding(argocd_bootstrap_name)
        except Exception as e:
            click.echo("Could not clean up ArgoCD bootstrap temporary resources, manual clean-up is required")

        # wait for ArgoCD to be ready

        argocd_ss = kube_client.get_stateful_set_objects(ARGOCD_NAMESPACE, "argocd-application-controller")
        kube_client.wait_for_stateful_set(argocd_ss)

        # 	argocd-server
        argocd_server = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-server")
        kube_client.wait_for_deployment(argocd_server)

        # wait for additional ArgoCD Pods to transition to Running
        # this is related to a condition where apps attempt to deploy before
        # repo, redis, or other health checks are passing
        # this can cause future steps to break since the registry app
        # may never apply

        # 	argocd-repo-server
        argocd_repo_server = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-repo-server")
        kube_client.wait_for_deployment(argocd_repo_server)

        # HA components

        # argocd-redis-ha-haproxy Deployment
        argocd_redis_ha_haproxy = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-redis-ha-haproxy")
        kube_client.wait_for_deployment(argocd_redis_ha_haproxy)

        # argocd-redis-ha StatefulSet
        cert_manager = kube_client.get_stateful_set_objects(ARGOCD_NAMESPACE, "argocd-redis-ha-server")
        kube_client.wait_for_stateful_set(cert_manager)

        # create additional namespaces
        kube_client.create_namespace(ARGO_WORKFLOW_NAMESPACE)
        kube_client.create_namespace(ATLANTIS_NAMESPACE)
        kube_client.create_namespace(EXTERNAL_SECRETS_OPERATOR_NAMESPACE)

        # create additional service accounts
        kube_client.create_service_account(ATLANTIS_NAMESPACE, "atlantis")
        kube_client.create_service_account(EXTERNAL_SECRETS_OPERATOR_NAMESPACE, "external-secrets")

        # create argocd kubernetes project and secret for connectivity to private gitops repos
        annotations = {"managed-by": "argocd.argoproj.io"}

        # credentials template
        git_wildcard_url = "".join(p.parameters["<GIT_REPOSITORY_GIT_URL>"].partition("/")[:-1])

        argocd_sec_secret_name = f'{p.parameters["<GIT_ORGANIZATION_NAME>"]}-repo-creds'.lower()
        argocd_secret = {
            "type": "git",
            "name": argocd_sec_secret_name,
            "url": git_wildcard_url,
            "sshPrivateKey": p.internals["DEFAULT_SSH_PRIVATE_KEY"],
        }
        creds_labels = {"argocd.argoproj.io/secret-type": "repo-creds"}

        kube_client.create_plain_secret(ARGOCD_NAMESPACE,
                                        argocd_sec_secret_name,
                                        argocd_secret,
                                        annotations,
                                        creds_labels)

        # repo
        argocd_sec_project_name = f'{p.parameters["<GIT_ORGANIZATION_NAME>"]}-gitops'.lower()
        argocd_project = {
            "type": "git",
            "name": argocd_sec_project_name,
            "url": p.parameters["<GIT_REPOSITORY_GIT_URL>"],
        }
        repo_labels = {"argocd.argoproj.io/secret-type": "repository"}

        kube_client.create_plain_secret(ARGOCD_NAMESPACE,
                                        argocd_sec_project_name,
                                        argocd_project,
                                        annotations,
                                        repo_labels)

        # TODO: properly init harbor auth
        harbor_reg_url = p.parameters["<REGISTRY_REGISTRY_URL>"]
        registry_auth_method = {"username": p.internals["REGISTRY_ROBO_USER"],
                                "password": p.internals["REGISTRY_ROBO_USER_PASSWORD"],
                                "auth": p.internals["REGISTRY_ROBO_USER_AUTH"]
                                }

        registry_secret = {
            "config.json": json.dumps({"auths": {harbor_reg_url: {"auth": registry_auth_method}}})
        }

        kube_client.create_plain_secret(ARGO_WORKFLOW_NAMESPACE, "docker-config", registry_secret)
        # TODO: figure out if we need it
        # kube_client.create_plain_secret(ARGO_WORKFLOW_NAMESPACE, "registry-auth", registry_secret)

        # argocd pods are ready, get and set credentials
        argo_pas = kube_client.get_secret(ARGOCD_NAMESPACE, "argocd-initial-admin-secret")
        p.internals["ARGOCD_USER"] = "admin"
        p.internals["ARGOCD_PASSWORD"] = argo_pas

        time.sleep(30)

        # get argocd auth token
        with portforward.forward(ARGOCD_NAMESPACE, "argocd-server", 8080, 8080,
                                 config_path=p.internals["KCTL_CONFIG_PATH"], waiting=3):
            argocd_token = get_argocd_token(p.internals["ARGOCD_USER"], p.internals["ARGOCD_PASSWORD"])
            p.internals["ARGOCD_TOKEN"] = argocd_token

        click.echo("applying the registry application to argocd")

        # create argocd "core" project
        # TODO: explicitly whitelist project repositories
        cd_man.create_project(argocd_core_project_name, [
            p.parameters["<GIT_REPOSITORY_GIT_URL>"],
            "https://charts.jetstack.io",
            "https://kubernetes-sigs.github.io/external-dns",
            "*"
        ])

        # deploy registry app
        cd_man.create_core_application(argocd_core_project_name, p.parameters["<GIT_REPOSITORY_GIT_URL>"])

        p.set_checkpoint("k8s-delivery")
        p.save_checkpoint()

        click.echo("Installing ArgoCD. Done!")
    else:
        click.echo("Skipped ArgoCD installation.")

    # initialize and unseal vault
    if not p.has_checkpoint("secrets-management"):
        click.echo("Initializing Secrets Manager...")

        # need to wait here as vault is not available just after argo app deployment
        time.sleep(30)

        # wait for cert manager as it's created just before vault
        cert_manager = kube_client.get_deployment("cert-manager", "cert-manager")
        kube_client.wait_for_deployment(cert_manager)

        time.sleep(60)

        # wait for vault readiness
        try:
            vault_ss = kube_client.get_stateful_set_objects(VAULT_NAMESPACE, "vault")
        except Exception as e:
            raise click.ClickException("Vault service creation taking longer than expected. Please verify manually "
                                       "and restart")
        kube_client.wait_for_stateful_set(vault_ss, 600, wait_availability=False)

        # Vault init from the UI/API is broken from Vault version 1.12.0 till now 1.14.4
        # https://discuss.hashicorp.com/t/cant-init-1-13-2-with-awskms/54000
        # Workaround init using kubectl
        # with portforward.forward(VAULT_NAMESPACE, "vault-0", 8200, 8200,
        #                          config_path=p.internals["KCTL_CONFIG_PATH"]):
        #
        #     vault_client = hvac.Client(url='http://127.0.0.1:8200')
        #     if not vault_client.sys.is_initialized():
        #         vault_init_result = vault_client.sys.initialize()
        #         vault_root_token = vault_init_result['root_token']
        #         vault_keys = vault_init_result['keys']
        #
        #     if vault_client.sys.is_sealed():
        #         vault_secret = {
        #             "root-token": vault_root_token
        #         }
        #         for i, x in enumerate(vault_keys):
        #             vault_secret[f"root-unseal-key-{i}"] = x
        #         kube_client.create_plain_secret("vault", "vault-unseal-secret", vault_secret)

        time.sleep(15)
        try:
            out = kctl.exec("vault-0", "-- vault operator init", namespace=VAULT_NAMESPACE)
        except Exception as e:
            raise click.ClickException("Could not unseal vault")

        vault_keys = re.findall("^Recovery\\sKey\\s(?P<index>\\d):\\s(?P<key>.+)$", out, re.MULTILINE)
        vault_root_token = re.findall("^Initial\\sRoot\\sToken:\\s(?P<token>.+)$", out, re.MULTILINE)

        if not vault_root_token:
            raise click.ClickException("Could not unseal vault")

        vault_secret = {
            "root-token": vault_root_token[0]
        }
        for i, v in vault_keys:
            vault_secret[f"root-unseal-key-{i}"] = v

        kube_client.create_plain_secret("vault", "vault-unseal-secret", vault_secret)
        p.internals["VAULT_ROOT_TOKEN"] = vault_root_token[0]

        p.set_checkpoint("secrets-management")
        p.save_checkpoint()

        click.echo("Vault initialization. Done!")

        time.sleep(15)
    else:
        click.echo("Skipped Secrets Manager initialization.")

    if not p.has_checkpoint("secrets-management-tf"):
        click.echo("Setting Secrets...")

        ingress = kube_client.get_ingress("vault", "vault")
        kube_client.wait_for_ingress(ingress)

        # run security manager tf to create secrets and roles
        sec_man_tf_env_vars = {
            **{
                "VAULT_TOKEN": p.internals["VAULT_ROOT_TOKEN"],
                "VAULT_ADDR": f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
            },
            **cloud_provider_auth_env_vars}
        # set envs as required by tf
        set_envs(sec_man_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_SECRETS_MANAGER)
        tf_wrapper.init()
        tf_wrapper.apply({
            "vcs_bot_ssh_public_key": p.internals["DEFAULT_SSH_PUBLIC_KEY"],
            "vcs_bot_ssh_private_key": p.internals["DEFAULT_SSH_PRIVATE_KEY"],
            "b64_docker_auth": p.internals["REGISTRY_ROBO_USER_AUTH"],
            "vcs_token": p.internals["GIT_ACCESS_TOKEN"],
            "atlantis_repo_webhook_secret": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"],
            "atlantis_repo_webhook_url": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_URL>"],
            "vault_token": p.internals["VAULT_ROOT_TOKEN"]
        })
        sec_man_out = tf_wrapper.output()

        # unset envs as no longer needed
        unset_envs(sec_man_tf_env_vars)

        kube_client.create_configmap(VAULT_NAMESPACE, "vault-init", {})

        p.set_checkpoint("secrets-management-tf")
        p.save_checkpoint()
        click.echo("Secrets set. Done!")

    else:
        click.echo("Skipped setting Secrets.")

    if not p.has_checkpoint("users-tf"):
        click.echo("Provisioning Users...")

        # run security manager tf to create secrets and roles
        user_man_tf_env_vars = {
            **{
                "GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
                "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME),
                "VAULT_TOKEN": p.internals["VAULT_ROOT_TOKEN"],
                "VAULT_ADDR": f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
            },
            **cloud_provider_auth_env_vars}
        # set envs as required by tf
        set_envs(user_man_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_USERS)
        tf_wrapper.init()
        tf_wrapper.apply()
        user_man_out = tf_wrapper.output()

        # unset envs as no longer needed
        unset_envs(user_man_tf_env_vars)

        p.set_checkpoint("users-tf")
        p.save_checkpoint()
        click.echo("Users provisioning. Done!")

    else:
        click.echo("Skipped provisioning Users.")

    # TODO: commit changes

    return True


def set_envs(env_vars):
    for k, vault_i in env_vars.items():
        os.environ[k] = vault_i


def unset_envs(env_vars):
    for k in env_vars.keys():
        os.environ.pop(k)


def prepare_parameters(p):
    # TODO: move to appropriate place
    p.parameters["<OWNER_EMAIL>"] = p.get_input_param(OWNER_EMAIL)
    p.parameters["<CLOUD_PROVIDER>"] = p.cloud_provider
    p.parameters["<PRIMARY_CLUSTER_NAME>"] = p.get_input_param(PRIMARY_CLUSTER_NAME)
    p.parameters["<GIT_PROVIDER>"] = p.git_provider
    p.internals["GIT_ACCESS_TOKEN"] = p.get_input_param(GIT_ACCESS_TOKEN)
    p.parameters["<GITOPS_REPOSITORY_NAME>"] = p.get_input_param(GITOPS_REPOSITORY_NAME)
    p.parameters["<GIT_ORGANIZATION_NAME>"] = p.get_input_param(GIT_ORGANIZATION_NAME)
    p.parameters["<DOMAIN_NAME>"] = p.get_input_param(DOMAIN_NAME)
    p.parameters["<GIT_REPOSITORY_ROOT>"] = f'github.com/{p.get_input_param(GIT_ORGANIZATION_NAME)}'
    p.parameters["<KUBECTL_VERSION>"] = KUBECTL_VERSION

    # prepare registry machine user
    robo_user_name = "robot@robo-main"
    p.internals["REGISTRY_ROBO_USER"] = robo_user_name
    if "REGISTRY_ROBO_USER_SECRET" not in p.parameters:
        p.internals["REGISTRY_ROBO_USER_PASSWORD"] = random_string_generator(20)

    robo_auth = f'{robo_user_name}:{p.internals["REGISTRY_ROBO_USER_PASSWORD"]}'
    p.internals["REGISTRY_ROBO_USER_AUTH"] = base64.b64encode(robo_auth.encode("utf-8")).decode("utf-8")

    # set IaC webhook secret
    if "<IAC_PR_AUTOMATION_WEBHOOK_SECRET>" not in p.parameters:
        p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"] = random_string_generator(20)

    # Ingress URLs for core components. Note!: URL does not contain protocol
    cluster_fqdn = f'{p.get_input_param(DOMAIN_NAME)}'
    p.parameters["<CC_CLUSTER_FQDN>"] = cluster_fqdn
    p.parameters["<SECRET_MANAGER_INGRESS_URL>"] = f'vault.{cluster_fqdn}'
    p.parameters["<CD_INGRESS_URL>"] = f'argocd.{cluster_fqdn}'
    p.parameters["<CI_INGRESS_URL>"] = f'argo.{cluster_fqdn}'
    p.parameters["<IAC_PR_AUTOMATION_INGRESS_URL>"] = f'atlantis.{cluster_fqdn}'
    p.parameters["<REGISTRY_INGRESS_URL>"] = f'harbor.{cluster_fqdn}'
    p.parameters["<GRAFANA_INGRESS_URL>"] = f'grafana.{cluster_fqdn}'
    p.parameters["<SONARQUBE_INGRESS_URL>"] = f'sonarqube.{cluster_fqdn}'

    # OIDC config
    sec_man_ing = f'{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}'
    p.parameters["<OIDC_PROVIDER_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx'
    p.parameters["<OIDC_PROVIDER_AUTHORIZE_URL>"] = f'{sec_man_ing}/ui/vault/identity/oidc/provider/cgdevx/authorize'
    p.parameters["<OIDC_PROVIDER_TOKEN_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx/token'
    p.parameters["<OIDC_PROVIDER_USERINFO_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx/userinfo'
    p.parameters["<CD_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<CD_INGRESS_URL>"]}/auth/callback'
    p.parameters["<CI_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<CI_INGRESS_URL>"]}/oauth2/callback'
    p.parameters["<REGISTRY_REGISTRY_URL>"] = f'{p.parameters["<REGISTRY_INGRESS_URL>"]}'
    p.parameters[
        "<IAC_PR_AUTOMATION_WEBHOOK_URL>"] = f'https://{p.parameters["<IAC_PR_AUTOMATION_INGRESS_URL>"]}/events'

    return p


def cloud_provider_check(manager: CloudProviderManager, p: StateStore) -> None:
    if not manager.detect_cli_presence():
        raise click.ClickException("Cloud CLI is missing")
    if not manager.evaluate_permissions():
        raise click.ClickException("Insufficient IAM permission")


def git_provider_check(manager: GitProviderManager, p: StateStore) -> None:
    if not manager.evaluate_permissions():
        raise click.ClickException("Insufficient Git token permissions")
    if manager.check_repository_existence(p.get_input_param(GITOPS_REPOSITORY_NAME)):
        raise click.ClickException("GitOps repo already exists")


def dns_provider_check(manager: DNSManager, p: StateStore) -> None:
    if not manager.evaluate_permissions():
        raise click.ClickException("Insufficient DNS permissions")
    if not manager.evaluate_domain_ownership(p.get_input_param(DOMAIN_NAME)):
        raise click.ClickException("Could not verify domain ownership")


def setup_param_validator(params: StateStore) -> bool:
    if params.dns_registrar is None:
        if params.cloud_provider == CloudProviders.AWS:
            params.dns_registrar = DnsRegistrars.Route53
        if params.cloud_provider == CloudProviders.Azure:
            params.dns_registrar = DnsRegistrars.AzureDNS

    # TODO: validate parameters
    if (params.cloud_provider != CloudProviders.Azure and
            (params.get_input_param(CLOUD_PROFILE) is None
             or params.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY) is not None
             or params.get_input_param(
                        CLOUD_ACCOUNT_ACCESS_SECRET) is not None)
            and
            (params.get_input_param(CLOUD_PROFILE) is not None
             or params.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY) is None
             or params.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET) is None)):
        click.echo("Cloud account keys validation error: should specify only one of profile or key + secret")
        return False

    return True
