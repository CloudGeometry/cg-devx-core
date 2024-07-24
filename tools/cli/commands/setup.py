import re
import time
import webbrowser

import click
import hvac
import yaml
from alive_progress import alive_bar
from typing import List
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, \
    LOCAL_TF_FOLDER_SECRETS_MANAGER, LOCAL_TF_FOLDER_USERS, LOCAL_TF_FOLDER_CORE_SERVICES
from common.const.const import GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH, KUBECTL_VERSION, PLATFORM_USER_NAME, \
    TERRAFORM_VERSION, GITHUB_TF_REQUIRED_PROVIDER_VERSION, GITLAB_TF_REQUIRED_PROVIDER_VERSION
from common.const.namespaces import ARGOCD_NAMESPACE, ARGO_WORKFLOW_NAMESPACE, EXTERNAL_SECRETS_OPERATOR_NAMESPACE, \
    ATLANTIS_NAMESPACE, VAULT_NAMESPACE, HARBOR_NAMESPACE, SONARQUBE_NAMESPACE
from common.const.parameter_names import CLOUD_PROFILE, OWNER_EMAIL, CLOUD_PROVIDER, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, CLOUD_REGION, PRIMARY_CLUSTER_NAME, DNS_REGISTRAR, DNS_REGISTRAR_ACCESS_TOKEN, \
    DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET, DOMAIN_NAME, GIT_PROVIDER, GIT_ORGANIZATION_NAME, \
    GIT_ACCESS_TOKEN, GITOPS_REPOSITORY_NAME, GITOPS_REPOSITORY_TEMPLATE_URL, GITOPS_REPOSITORY_TEMPLATE_BRANCH, \
    DEMO_WORKLOAD, OPTIONAL_SERVICES
from common.enums.cloud_providers import CloudProviders
from common.enums.dns_registrars import DnsRegistrars
from common.enums.git_providers import GitProviders
from common.logging_config import configure_logging
from common.state_store import StateStore
from common.tracing_decorator import trace
from common.utils.command_utils import init_cloud_provider, init_git_provider, prepare_cloud_provider_auth_env_vars, \
    set_envs, unset_envs, wait, wait_http_endpoint_readiness, prepare_git_provider_env_vars
from common.utils.generators import random_string_generator
from common.utils.k8s_utils import find_pod_by_name_fragment, get_kr8s_pod_instance_by_name
from common.utils.optional_services_manager import OptionalServices, build_argo_exclude_string
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.dependency_manager import DependencyManager
from services.dns.dns_provider_manager import DNSManager
from services.k8s.config_builder import create_k8s_config, write_k8s_config
from services.k8s.delivery_service_manager import DeliveryServiceManager, get_argocd_token
from services.k8s.k8s import KubeClient, write_ca_cert
from services.k8s.kctl_wrapper import KctlWrapper
from services.keys.key_manager import KeyManager
from services.platform_template_manager import GitOpsTemplateManager
from services.tf_wrapper import TfWrapper
from services.vcs.git_provider_manager import GitProviderManager


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
              is_flag=True)
@click.option('--optional-services', '-ops', 'optional_services', help='Optional services', type=click.STRING,
              multiple=True)
@click.option('--config-file', '-f', 'config', help='Load parameters from file', type=click.File(mode='r'))
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def setup(
        email: str, cloud_provider: CloudProviders, cloud_profile: str, cloud_key: str, cloud_secret: str,
        cloud_region: str, cluster_name: str, dns_reg: DnsRegistrars, dns_reg_token: str,
        dns_reg_key: str, dns_reg_secret: str, domain: str, git_provider: GitProviders, git_org: str, git_token: str,
        gitops_repo_name: str, gitops_template_url: str, gitops_template_branch: str, install_demo: bool,
        optional_services: List[str], config: click.File, verbosity: str
):
    """Creates new CG DevX installation."""
    click.echo("Setup CG DevX installation...")
    # Initialize the start time to measure the duration of the platform setup
    func_start_time = time.time()

    # Set up global logger
    configure_logging(verbosity)

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
            DEMO_WORKLOAD: install_demo,
            OPTIONAL_SERVICES: optional_services
        })

    # validate parameters
    if not p.validate_input_params(validator=setup_param_validator):
        raise click.ClickException("Input parameters are incorrect")

    cloud_man, dns_man = init_cloud_provider(p)

    p.parameters["<CLOUD_REGION>"] = cloud_man.region
    p.internals["CLOUD_ACCOUNT"] = cloud_man.account

    git_man = init_git_provider(p)

    if not p.has_checkpoint("preflight"):
        click.echo("1/12: Executing pre-flight checks...")

        cloud_provider_check(cloud_man, p)
        click.echo("Cloud provider pre-flight check. Done!")

        git_provider_check(git_man, p)
        click.echo("Git provider pre-flight check. Done!")

        git_user_login, git_user_name, git_user_email = git_man.get_current_user_info()
        p.internals["GIT_USER_LOGIN"] = git_user_login
        p.parameters["<GIT_USER_LOGIN>"] = git_user_login
        p.internals["GIT_USER_NAME"] = git_user_name
        p.parameters["<GIT_USER_NAME>"] = git_user_name
        p.internals["GIT_USER_EMAIL"] = git_user_email
        p.parameters["<GIT_USER_EMAIL>"] = git_user_email
        p.fragments["# <GIT_PROVIDER_MODULE>"] = git_man.create_tf_module_snippet()
        p.fragments["# <GIT_REQUIRED_PROVIDER>"] = git_man.create_tf_required_provider_snippet()
        p.parameters["<GITHUB_PROVIDER_VERSION>"] = GITHUB_TF_REQUIRED_PROVIDER_VERSION
        p.parameters["<GITLAB_PROVIDER_VERSION>"] = GITLAB_TF_REQUIRED_PROVIDER_VERSION

        git_subscription_plan = git_man.get_organization_plan()
        p.parameters["<GIT_SUBSCRIPTION_PLAN>"] = str(bool(git_subscription_plan)).lower()
        if git_subscription_plan > 0:
            p.fragments["# <GIT_RUNNER_GROUP>"] = git_man.create_runner_group_snippet()
            p.parameters["<GIT_RUNNER_GROUP_NAME>"] = p.get_input_param(PRIMARY_CLUSTER_NAME)
        else:
            # match the GitHub's default runner group
            p.parameters["<GIT_RUNNER_GROUP_NAME>"] = "Default"

        dns_provider_check(dns_man, p)
        click.echo("DNS provider pre-flight check. Done!")

        p.set_checkpoint("preflight")
        p.save_checkpoint()
        click.echo("1/12: Pre-flight checks. Done!")

    # end preflight check section
    else:
        click.echo("1/12: Skipped pre-flight checks.")

    dep_man: DependencyManager = DependencyManager()

    if not p.has_checkpoint("dependencies"):
        click.echo("2/12: Dependencies check...")

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

        click.echo("2/12: Dependencies check. Done!")
        p.set_checkpoint("dependencies")
        p.save_checkpoint()
    else:
        click.echo("2/12: Skipped dependencies check.")

    # promote input params
    prepare_parameters(p)
    p.save_checkpoint()

    tm = GitOpsTemplateManager(p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_URL),
                               p.get_input_param(GITOPS_REPOSITORY_TEMPLATE_BRANCH),
                               p.get_input_param(GIT_ACCESS_TOKEN))

    if not p.has_checkpoint("one-time-setup"):
        click.echo("3/12: Setting initial parameters...")

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

        tf_backend_storage, key = cloud_man.create_iac_state_storage(p.get_input_param(GITOPS_REPOSITORY_NAME))
        p.internals["TF_BACKEND_STORAGE_ACCESS_KEY"] = key
        p.internals["TF_BACKEND_STORAGE_NAME"] = tf_backend_storage

        p.fragments["# <TF_VCS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                        "vcs")
        p.fragments["# <TF_HOSTING_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                            "hosting_provider")
        p.fragments["# <TF_SECRETS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                            "secrets")
        p.fragments["# <TF_USERS_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                          "users")
        p.fragments["# <TF_CORE_SERVICES_REMOTE_BACKEND>"] = cloud_man.create_iac_backend_snippet(tf_backend_storage,
                                                                                                  "core_services")

        p.fragments["# <TF_HOSTING_PROVIDER>"] = cloud_man.create_hosting_provider_snippet()

        p.fragments["# <IAC_PR_AUTOMATION_CONFIG>"] = cloud_man.create_iac_pr_automation_config_snippet()

        p.parameters["<K8S_ROLE_MAPPING>"] = cloud_man.create_k8s_cluster_role_mapping_snippet()

        p.fragments["# <ADDITIONAL_LABELS>"] = cloud_man.create_additional_labels()
        p.fragments["# <BASE_ADDITIONAL_ANNOTATIONS>"] = cloud_man.create_additional_labels()
        p.fragments["# <INGRESS_ANNOTATIONS>"] = cloud_man.create_ingress_annotations()
        p.fragments["# <SIDECAR_ANNOTATION>"] = cloud_man.create_sidecar_annotation()

        p.fragments["# <KUBECOST_CLOUD_PROVIDER_CONFIGURATION>"] = cloud_man.create_kubecost_annotation()
        p.fragments["# <GPU_OPERATOR_ADDITIONAL_PARAMETERS>"] = cloud_man.create_gpu_operator_parameters()

        # dns zone info for external dns
        dns_zone_name, is_dns_zone_private = dns_man.get_domain_zone(p.parameters["<DOMAIN_NAME>"])
        p.internals["DNS_ZONE_NAME"] = dns_zone_name
        p.internals["DNS_ZONE_IS_PRIVATE"] = is_dns_zone_private

        p.fragments["# <EXTERNAL_DNS_ADDITIONAL_CONFIGURATION>"] = cloud_man.create_external_secrets_config(
            location=dns_zone_name, is_private=is_dns_zone_private)

        click.echo("Creating tf backend storage. Done!")

        p.set_checkpoint("one-time-setup")
        p.save_checkpoint()
        click.echo("3/12: Setting initial parameters. Done!")

    # end preflight check section
    else:
        click.echo("3/12: Skipped setting initial parameters.")

    if not p.has_checkpoint("repo-prep"):
        click.echo("4/12: Preparing your GitOps code...")

        tm.check_repository_existence()
        tm.clone()
        tm.build_repo_from_template()
        tm.parametrise_tf(p)

        p.set_checkpoint("repo-prep")
        p.save_checkpoint()

        click.echo("4/12: Preparing your GitOps code. Done!")
    else:
        click.echo("4/12: Skipped GitOps code prep.")

    # VCS provisioning
    cloud_provider_auth_env_vars = prepare_cloud_provider_auth_env_vars(p)
    git_provider_env_vars = prepare_git_provider_env_vars(p)

    # VCS section
    if not p.has_checkpoint("vcs-tf"):
        click.echo("5/12: Provisioning VCS...")
        # vcs env vars
        vcs_tf_env_vars = {
            **cloud_provider_auth_env_vars,
            **git_provider_env_vars
        }

        # set envs as required by tf
        set_envs(vcs_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.apply({"atlantis_repo_webhook_secret": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"],
                          "cd_webhook_secret": p.parameters["<CD_PUSH_EVENT_WEBHOOK_SECRET>"],
                          "vcs_bot_ssh_public_key": p.parameters["<VCS_BOT_SSH_PUBLIC_KEY>"]})
        vcs_out = tf_wrapper.output()

        # store out params
        p.parameters["<GIT_REPOSITORY_GIT_URL>"] = vcs_out["gitops_repo_ssh_clone_url"]
        p.parameters["<GIT_REPOSITORY_URL>"] = vcs_out["gitops_repo_html_url"]

        # unset envs as no longer needed
        unset_envs(vcs_tf_env_vars)

        p.set_checkpoint("vcs-tf")
        p.save_checkpoint()

        click.echo("5/12: Provisioning VCS. Done!")
    else:
        click.echo("5/12: Skipped VCS provisioning.")

    # K8s Cluster section
    if not p.has_checkpoint("k8s-tf"):
        click.echo("6/12: Provisioning K8s cluster...")

        # run hosting provider tf to create K8s cluster
        hp_tf_env_vars = {
            **{},  # add vars here
            **cloud_provider_auth_env_vars}
        # set envs as required by tf
        set_envs(hp_tf_env_vars)

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_HOSTING_PROVIDER)
        tf_wrapper.init()
        tf_wrapper.apply({"cluster_ssh_public_key": p.parameters.get("<CC_CLUSTER_SSH_PUBLIC_KEY>", "")})
        hp_out = tf_wrapper.output()

        # store out params
        # network
        p.parameters["<NETWORK_ID>"] = hp_out["network_id"]
        # roles
        p.parameters["<CI_IAM_ROLE_RN>"] = hp_out["iam_ci_role"]
        p.parameters["<IAC_PR_AUTOMATION_IAM_ROLE_RN>"] = hp_out["iac_pr_automation_role"]
        p.parameters["<CERT_MANAGER_IAM_ROLE_RN>"] = hp_out["cert_manager_role"]
        p.parameters["<EXTERNAL_DNS_IAM_ROLE_RN>"] = hp_out["external_dns_role"]
        p.parameters["<SECRET_MANAGER_IAM_ROLE_RN>"] = hp_out["secret_manager_role"]
        p.parameters["<CLUSTER_AUTOSCALER_IAM_ROLE_RN>"] = hp_out["cluster_autoscaler_role"]
        # cluster
        p.internals["CC_CLUSTER_ENDPOINT"] = hp_out["cluster_endpoint"]
        p.internals["CC_CLUSTER_CA_CERT_DATA"] = hp_out["cluster_certificate_authority_data"]
        p.internals["CC_CLUSTER_CA_CERT_PATH"] = write_ca_cert(hp_out["cluster_certificate_authority_data"])
        p.internals["CC_CLUSTER_OIDC_ISSUER_URL"] = hp_out["cluster_oidc_issuer_url"]

        # generate cluster autoscaler config here as it could depend on node groups configuration
        p.fragments["# <K8S_AUTOSCALER>"] = cloud_man.create_autoscaler_snippet(
            p.parameters["<PRIMARY_CLUSTER_NAME>"],
            hp_out["cluster_node_groups"]
        )

        # artifact storage
        p.parameters["<CLOUD_BINARY_ARTIFACTS_STORE>"] = hp_out["artifact_storage"]
        # kms keys
        sec_man_key = hp_out["secret_manager_seal_key"]
        p.parameters["<SECRET_MANAGER_SEAL_RN>"] = sec_man_key
        # TODO: find a better way to pass cloud provider specific params
        p.fragments["# <SECRET_MANAGER_SEAL>"] = cloud_man.create_seal_snippet(sec_man_key,
                                                                               name=p.parameters[
                                                                                   "<PRIMARY_CLUSTER_NAME>"])

        # unset envs as no longer needed
        unset_envs(hp_tf_env_vars)

        if p.cloud_provider == CloudProviders.AWS:
            # user could get kubeconfig by running command
            # `aws eks update-kubeconfig --region region-code --name my-cluster --kubeconfig my-config-path`
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
            p.parameters["<CC_CLUSTER_OIDC_PROVIDER>"] = hp_out["cluster_oidc_provider_arn"]
        elif p.cloud_provider == CloudProviders.Azure:
            # user could get kubeconfig by running command
            # `az aks get-credentials --name my-cluster --resource-group my-rg --admin`
            # get config from tf output
            kctl_config_path = write_k8s_config(hp_out["kube_config_raw"])

        p.internals["KCTL_CONFIG_PATH"] = kctl_config_path

        p.set_checkpoint("k8s-tf")
        p.save_checkpoint()

        click.echo("6/12: Provisioning K8s cluster. Done!")
    else:
        click.echo("6/12: Skipped K8s provisioning.")

    if not p.has_checkpoint("gitops-vcs"):
        click.echo("7/12: Pushing GitOps code...")

        tm.parametrise(p)

        tm.upload(p.parameters["<GIT_REPOSITORY_GIT_URL>"],
                  p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
                  p.internals["GIT_USER_NAME"],
                  p.internals["GIT_USER_EMAIL"])

        p.set_checkpoint("gitops-vcs")
        p.save_checkpoint()

        click.echo("7/12: Pushing GitOps code. Done!")
    else:
        click.echo("7/12: Skipped GitOps repo initialization.")

    # install ArgoCD
    if not p.has_checkpoint("k8s-delivery"):
        click.echo("8/12: Installing ArgoCD...")
        with alive_bar(20, title='ArgoCD Installation Progress') as bar:

            kube_client = init_k8s_client(cloud_man, p)
            cd_man = DeliveryServiceManager(kube_client)
            bar()

            argocd_bootstrap_name = "argocd-bootstrap"
            argocd_core_project_name = "core"

            # get CoreDNS deployments to validate cluster
            coredns_deployment = kube_client.get_deployment("kube-system", "coredns")
            bar()

            # wait for deployment readiness
            kube_client.wait_for_deployment(coredns_deployment)
            bar()  # Add a few here

            kube_client.create_namespace(ARGOCD_NAMESPACE)
            bar()
            kube_client.create_service_account(ARGOCD_NAMESPACE, argocd_bootstrap_name)
            bar()
            kube_client.create_cluster_role(ARGOCD_NAMESPACE, argocd_bootstrap_name)
            bar()

            kube_client.create_cluster_role_binding(ARGOCD_NAMESPACE, argocd_bootstrap_name, argocd_bootstrap_name)
            bar()

            job = cd_man.create_argocd_bootstrap_job(argocd_bootstrap_name)
            kube_client.wait_for_job(job)
            bar()  # Add a few here
            # cleanup temp resources
            try:
                kube_client.remove_service_account(ARGOCD_NAMESPACE, argocd_bootstrap_name)
                kube_client.remove_cluster_role(argocd_bootstrap_name)
                kube_client.remove_cluster_role_binding(argocd_bootstrap_name)
            except Exception as e:
                click.echo("Could not clean up ArgoCD bootstrap temporary resources, manual clean-up is required")
            bar()

            # wait for ArgoCD to be ready

            argocd_ss = kube_client.get_stateful_set_objects(ARGOCD_NAMESPACE, "argocd-application-controller")
            kube_client.wait_for_stateful_set(argocd_ss)
            bar()

            # 	argocd-server
            argocd_server = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-server")
            kube_client.wait_for_deployment(argocd_server)
            bar()  # add a few here
            # wait for additional ArgoCD Pods to transition to Running
            # this is related to a condition where apps attempt to deploy before
            # repo, redis, or other health checks are passing
            # this can cause future steps to break since the registry app
            # may never apply

            # 	argocd-repo-server
            argocd_repo_server = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-repo-server")
            kube_client.wait_for_deployment(argocd_repo_server)
            bar()

            # HA components

            # argocd-redis-ha-haproxy Deployment
            argocd_redis_ha_haproxy = kube_client.get_deployment(ARGOCD_NAMESPACE, "argocd-redis-ha-haproxy")
            kube_client.wait_for_deployment(argocd_redis_ha_haproxy)
            bar()

            # argocd-redis-ha StatefulSet
            cert_manager = kube_client.get_stateful_set_objects(ARGOCD_NAMESPACE, "argocd-redis-ha-server")
            kube_client.wait_for_stateful_set(cert_manager)
            bar()

            # create additional namespaces
            kube_client.create_namespace(ARGO_WORKFLOW_NAMESPACE)
            kube_client.create_namespace(ATLANTIS_NAMESPACE)
            kube_client.create_namespace(EXTERNAL_SECRETS_OPERATOR_NAMESPACE)
            bar()

            # create additional service accounts
            kube_client.create_service_account(ATLANTIS_NAMESPACE, "atlantis")
            kube_client.create_service_account(EXTERNAL_SECRETS_OPERATOR_NAMESPACE, "external-secrets")
            bar()

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
            bar()

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
            bar()

            # argocd pods are ready, get and set credentials
            argo_pas = kube_client.get_secret(ARGOCD_NAMESPACE, "argocd-initial-admin-secret")
            p.internals["ARGOCD_USER"] = "admin"
            p.internals["ARGOCD_PASSWORD"] = argo_pas

            # get argocd auth token
            k8s_pod = find_pod_by_name_fragment(
                kube_config_path=p.internals["KCTL_CONFIG_PATH"],
                name_fragment="argocd-server",
                namespace=ARGOCD_NAMESPACE
            )
            kr8s_pod = get_kr8s_pod_instance_by_name(
                pod_name=k8s_pod.metadata.name,
                namespace=ARGOCD_NAMESPACE,
                kubeconfig=p.internals["KCTL_CONFIG_PATH"]
            )
            with kr8s_pod.portforward(remote_port=8080, local_port=8080):
                # Make an API request to the forwarded port
                argocd_token = get_argocd_token(p.internals["ARGOCD_USER"], p.internals["ARGOCD_PASSWORD"])
                p.internals["ARGOCD_TOKEN"] = argocd_token
            bar()
            # create argocd "core" project
            # TODO: explicitly whitelist project repositories
            cd_man.create_project(argocd_core_project_name, [
                p.parameters["<GIT_REPOSITORY_GIT_URL>"],
                "https://charts.jetstack.io",
                "https://kubernetes-sigs.github.io/external-dns",
                "*"
            ])

            # deploy registry app
            cd_man.create_core_application(argocd_core_project_name, p.parameters["<GIT_REPOSITORY_GIT_URL>"],
                                           p.parameters["<CD_SERVICE_EXCLUDE_LIST>"])
            bar()

            p.set_checkpoint("k8s-delivery")
            p.save_checkpoint()

        click.echo("8/12: Installing ArgoCD. Done!")
    else:
        click.echo("8/12: Skipped ArgoCD installation.")

    # initialize and unseal vault
    if not p.has_checkpoint("secrets-management"):
        click.echo("9/12: Initializing Secrets Manager...")
        with alive_bar(7, title='Initializing Secrets Manager') as bar:

            # default AWS EKS auth token life-time is 14m
            # to be safe should refresh token before proceeding
            kube_client = init_k8s_client(cloud_man, p)
            bar()

            # wait for cert manager as it's created just before vault
            cert_manager = kube_client.get_deployment("cert-manager", "cert-manager")
            kube_client.wait_for_deployment(cert_manager)
            bar()

            external_dns = kube_client.get_deployment("external-dns", "external-dns")
            kube_client.wait_for_deployment(external_dns)
            bar()

            external_dns = kube_client.get_deployment("ingress-nginx", "ingress-nginx-controller")
            kube_client.wait_for_deployment(external_dns)
            bar()

            # wait for vault readiness
            try:
                vault_ss = kube_client.get_stateful_set_objects(VAULT_NAMESPACE, "vault")
            except Exception as e:
                raise click.ClickException("Vault service creation taking longer than expected. Please verify manually "
                                           "and restart")
            kube_client.wait_for_stateful_set(vault_ss, 600, wait_availability=False)
            bar()

            # Vault init from the UI/API is broken from Vault version 1.12.0 till now 1.14.4
            # https://discuss.hashicorp.com/t/cant-init-1-13-2-with-awskms/54000
            # Workaround init using kubectl
            # with portforward.forward(VAULT_NAMESPACE, "vault-0", 8200, 8200,
            #                          config_path=p.internals["KCTL_CONFIG_PATH"], waiting=3,
            #                          log_level=portforward.LogLevel.ERROR:
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
            #         kube_client.create_plain_secret(VAULT_NAMESPACE, "vault-unseal-secret", vault_secret)

            # use k8s console client
            wait(30)
            kctl = KctlWrapper(p.internals["KCTL_CONFIG_PATH"])
            try:
                out = kctl.exec("vault-0", "-- vault operator init", container="vault", namespace=VAULT_NAMESPACE)
            except Exception as e:
                raise click.ClickException(f"Could not unseal vault: {e}")
            bar()

            vault_keys = re.findall("^Recovery\\sKey\\s(?P<index>\\d):\\s(?P<key>.+)$", out, re.MULTILINE)
            vault_root_token = re.findall("^Initial\\sRoot\\sToken:\\s(?P<token>.+)$", out, re.MULTILINE)

            if not vault_root_token:
                raise click.ClickException("Could not unseal vault")

            vault_secret = {
                "root-token": vault_root_token[0]
            }
            for i, v in vault_keys:
                vault_secret[f"root-unseal-key-{i}"] = v

            kube_client.create_plain_secret(VAULT_NAMESPACE, "vault-unseal-secret", vault_secret)
            bar()

        p.internals["VAULT_ROOT_TOKEN"] = vault_root_token[0]
        p.set_checkpoint("secrets-management")
        p.save_checkpoint()

        click.echo("9/12: Secrets Manager initialization. Done!")
    else:
        click.echo("9/12: Skipped Secrets Manager initialization.")

    if not p.has_checkpoint("secrets-management-tf"):
        click.echo("10/12: Setting Secrets...")

        with alive_bar(5, title='Secret Manager Pre-Deployment Readiness') as bar:
            # default AWS EKS auth token life-time is 14m
            # to be safe should refresh token before proceeding
            kube_client = init_k8s_client(cloud_man, p)
            bar()

            ingress = kube_client.get_ingress(VAULT_NAMESPACE, "vault")
            kube_client.wait_for_ingress(ingress)
            bar()

            tls_cert = kube_client.get_certificate(VAULT_NAMESPACE, "vault-tls")
            kube_client.wait_for_certificate(tls_cert)
            bar()

            wait_http_endpoint_readiness(f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}')
            bar()

            # run security manager tf to create secrets and roles
            sec_man_tf_env_vars = {
                **{
                    "VAULT_TOKEN": p.internals["VAULT_ROOT_TOKEN"],
                    "VAULT_ADDR": f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
                },
                **cloud_provider_auth_env_vars}
            # set envs as required by tf
            set_envs(sec_man_tf_env_vars)
            bar()

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_SECRETS_MANAGER)
        tf_wrapper.init()

        sec_man_tf_params = {
            "vcs_bot_ssh_public_key": p.internals["DEFAULT_SSH_PUBLIC_KEY"],
            "vcs_bot_ssh_private_key": p.internals["DEFAULT_SSH_PRIVATE_KEY"],
            "vcs_token": p.internals["GIT_ACCESS_TOKEN"],
            "cd_webhook_secret": p.parameters["<CD_PUSH_EVENT_WEBHOOK_SECRET>"],
            "atlantis_repo_webhook_secret": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"],
            "atlantis_repo_webhook_url": p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_URL>"],
            "vault_token": p.internals["VAULT_ROOT_TOKEN"],
            "cluster_endpoint": p.internals["CC_CLUSTER_ENDPOINT"],
        }
        if "<CC_CLUSTER_SSH_PUBLIC_KEY>" in p.parameters:
            sec_man_tf_params["cluster_ssh_public_key"] = p.parameters["<CC_CLUSTER_SSH_PUBLIC_KEY>"]

        if "TF_BACKEND_STORAGE_ACCESS_KEY" in p.internals:
            sec_man_tf_params["tf_backend_storage_access_key"] = p.internals["TF_BACKEND_STORAGE_ACCESS_KEY"]

        tf_wrapper.apply(sec_man_tf_params)

        sec_man_out = tf_wrapper.output()
        p.internals["REGISTRY_OIDC_CLIENT_ID"] = sec_man_out["registry_oidc_client_id"]
        p.internals["REGISTRY_OIDC_CLIENT_SECRET"] = sec_man_out["registry_oidc_client_secret"]
        p.internals["REGISTRY_ROBO_USER_PASSWORD"] = sec_man_out["registry_main_robot_user_password"]
        p.internals["REGISTRY_PASSWORD"] = sec_man_out["registry_admin_user_password"]
        p.internals["CODE_QUALITY_OIDC_CLIENT_ID"] = sec_man_out["code_quality_oidc_client_id"]
        p.internals["CODE_QUALITY_OIDC_CLIENT_SECRET"] = sec_man_out["code_quality_oidc_client_secret"]
        p.internals["CODE_QUALITY_PASSWORD"] = sec_man_out["code_quality_admin_user_password"]

        # prepare registry machine user
        robo_user_name = "robot@main-robot"
        p.internals["REGISTRY_ROBO_USER"] = robo_user_name

        # unset envs as no longer needed
        unset_envs(sec_man_tf_env_vars)

        kube_client.create_configmap(VAULT_NAMESPACE, "vault-init", {})

        p.set_checkpoint("secrets-management-tf")
        p.save_checkpoint()
        click.echo("10/12: Secrets set. Done!")

    else:
        click.echo("10/12: Skipped setting Secrets.")

    if not p.has_checkpoint("users-tf"):
        click.echo("11/12: Provisioning Users...")

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
        click.echo("11/12: Users provisioning. Done!")
    else:
        click.echo("11/12: Skipped provisioning Users.")

    if not p.has_checkpoint("core-services-tf"):
        click.echo("12/12: Configuring core services...")

        with alive_bar(9, title='Core Services Pre-Deployment Readiness') as bar:
            # default AWS EKS auth token life-time is 14m
            # to be safe should refresh token before proceeding
            kube_client = init_k8s_client(cloud_man, p)
            bar()

            # wait for harbor readiness
            harbor_dep = kube_client.get_deployment(HARBOR_NAMESPACE, "harbor-core")
            kube_client.wait_for_deployment(harbor_dep)
            bar()

            harbor_ingress = kube_client.get_ingress(HARBOR_NAMESPACE, "harbor-ingress")
            kube_client.wait_for_ingress(harbor_ingress)
            bar()

            harbor_tls_cert = kube_client.get_certificate(HARBOR_NAMESPACE, "harbor-tls")
            kube_client.wait_for_certificate(harbor_tls_cert)
            bar()

            # wait for sonarqube readiness
            sonar_ss = kube_client.get_stateful_set_objects(SONARQUBE_NAMESPACE, "sonarqube-sonarqube")
            kube_client.wait_for_stateful_set(sonar_ss)
            bar()

            sonar_ingress = kube_client.get_ingress(SONARQUBE_NAMESPACE, "sonarqube-sonarqube")
            kube_client.wait_for_ingress(sonar_ingress)
            bar()

            sonar_tls_cert = kube_client.get_certificate(SONARQUBE_NAMESPACE, "sonarqube-tls")
            kube_client.wait_for_certificate(sonar_tls_cert)
            bar()

            # wait for registry API endpoint readiness
            wait_http_endpoint_readiness(f'https://{p.parameters["<REGISTRY_INGRESS_URL>"]}')
            bar()

            p.internals["REGISTRY_USERNAME"] = "admin"
            # run security manager tf to create secrets and roles
            core_services_tf_env_vars = {
                **{
                    "HARBOR_URL": f'https://{p.parameters["<REGISTRY_INGRESS_URL>"]}',
                    "HARBOR_USERNAME": p.internals["REGISTRY_USERNAME"],
                    "HARBOR_PASSWORD": p.internals["REGISTRY_PASSWORD"],
                    "VAULT_TOKEN": p.internals["VAULT_ROOT_TOKEN"],
                    "VAULT_ADDR": f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
                },
                **cloud_provider_auth_env_vars}
            # set envs as required by tf
            set_envs(core_services_tf_env_vars)
            bar()

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_CORE_SERVICES)
        tf_wrapper.init()
        tf_wrapper.apply({
            "registry_oidc_client_id": p.internals["REGISTRY_OIDC_CLIENT_ID"],
            "registry_oidc_client_secret": p.internals["REGISTRY_OIDC_CLIENT_SECRET"],
            "registry_main_robot_password": p.internals["REGISTRY_ROBO_USER_PASSWORD"],
            "code_quality_oidc_client_id": p.internals["CODE_QUALITY_OIDC_CLIENT_ID"],
            "code_quality_oidc_client_secret": p.internals["CODE_QUALITY_OIDC_CLIENT_SECRET"],
            "code_quality_admin_password": p.internals["CODE_QUALITY_PASSWORD"]
        })
        core_services_out = tf_wrapper.output()
        p.parameters[
            "<REGISTRY_DOCKERHUB_PROXY>"] = f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{core_services_out["dockerhub_proxy_name"]}'
        p.parameters[
            "<REGISTRY_GCR_PROXY>"] = f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{core_services_out["gcr_proxy_name"]}'
        p.parameters[
            "<REGISTRY_K8S_GCR_PROXY>"] = f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{core_services_out["k8s_gcr_proxy_name"]}'
        p.parameters[
            "<REGISTRY_QUAY_PROXY>"] = f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{core_services_out["quay_proxy_name"]}'

        # unset envs as no longer needed
        unset_envs(core_services_tf_env_vars)

        p.set_checkpoint("core-services-tf")
        p.save_checkpoint()
        click.echo("12/12: Configuring core services. Done!")

    else:
        click.echo("12/12: Skipped core services configuration.")

    if not p.has_checkpoint("tf-store-hardening"):
        # restrict access to IaC remote state store
        cloud_man.protect_iac_state_storage(p.internals["TF_BACKEND_STORAGE_NAME"],
                                            p.parameters["<IAC_PR_AUTOMATION_IAM_ROLE_RN>"])
        p.set_checkpoint("tf-store-hardening")
        p.save_checkpoint()

    show_credentials(p)

    # Calculate the total seconds elapsed
    total_seconds = time.time() - func_start_time

    # Use divmod to separate the total seconds into minutes and seconds
    minutes, seconds = divmod(total_seconds, 60)

    # Display the result with minutes as integers and seconds with two decimal places
    click.echo(f"Platform setup completed in {int(minutes)} minutes, {int(seconds)} seconds")

    return True


@trace()
def init_k8s_client(cloud_man, p):
    if p.cloud_provider == CloudProviders.AWS:
        k8s_token = cloud_man.get_k8s_token(p.parameters["<PRIMARY_CLUSTER_NAME>"])
        kube_client = KubeClient(ca_cert_path=p.internals["CC_CLUSTER_CA_CERT_PATH"],
                                 api_key=k8s_token,
                                 endpoint=p.internals["CC_CLUSTER_ENDPOINT"])
    else:
        kube_client = KubeClient(config_file=p.internals["KCTL_CONFIG_PATH"])
    return kube_client


@trace()
def show_credentials(p):
    user_name = PLATFORM_USER_NAME
    vault_client = hvac.Client(url=f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
                               token=p.internals["VAULT_ROOT_TOKEN"])
    res = vault_client.secrets.kv.v2.read_secret(path=f"/{user_name}", mount_point='users/')
    if "data" in res:
        user_pass = res["data"]["data"]["initial-password"]

    click.secho('ATTENTION', blink=True, bold=True, bg="red", fg="black")
    click.secho("Below are the credentials to your platform services. Please store them securely.", bg="green",
                fg="blue")

    click.secho("Secrets manager", bg="green", fg="blue")
    click.secho(f'URL: https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}', bg="green", fg="blue")
    click.secho(f'Root login token: {p.internals["VAULT_ROOT_TOKEN"]}', bg="green", fg="blue")
    click.secho(f'CGDevX admin user login: {user_name} password: {user_pass}', bg="green", fg="blue")

    click.secho("Continuous Delivery system", bg="green", fg="blue")
    click.secho(f'URL: https://{p.parameters["<CD_INGRESS_URL>"]}', bg="green", fg="blue")
    click.secho(f'Admin login: {p.internals["ARGOCD_USER"]} password: {p.internals["ARGOCD_PASSWORD"]}', bg="green",
                fg="blue")

    click.secho(f'Kubeconfig file: {p.internals["KCTL_CONFIG_PATH"]}', bg="green", fg="blue")

    click.secho(
        f'Links to all core platform services could be found in your GitOps repo readme file at: {p.parameters["<GIT_REPOSITORY_URL>"]}',
        bg="green", fg="blue")
    webbrowser.open(f'{p.parameters["<GIT_REPOSITORY_URL>"]}', autoraise=False)

    return


@trace()
def prepare_parameters(p):
    # TODO: move to appropriate place

    exclude_string = build_argo_exclude_string(p.get_input_param(OPTIONAL_SERVICES))
    p.parameters["<CD_SERVICE_EXCLUDE_LIST>"] = exclude_string
    if exclude_string:
        p.fragments["# <CD_SERVICE_EXCLUDE_SNIPPET>"] = """directory:
          exclude: '{<CD_SERVICE_EXCLUDE_LIST>}'"""
    else:
        p.fragments["# <CD_SERVICE_EXCLUDE_SNIPPET>"] = ""

    p.parameters["<OWNER_EMAIL>"] = p.get_input_param(OWNER_EMAIL).lower()
    p.parameters["<CLOUD_PROVIDER>"] = p.cloud_provider
    p.parameters["<PRIMARY_CLUSTER_NAME>"] = p.get_input_param(PRIMARY_CLUSTER_NAME)
    p.parameters["<GIT_PROVIDER>"] = p.git_provider
    p.internals["GIT_ACCESS_TOKEN"] = p.get_input_param(GIT_ACCESS_TOKEN)
    p.parameters["<GITOPS_REPOSITORY_NAME>"] = p.get_input_param(GITOPS_REPOSITORY_NAME).lower()
    org_name = p.get_input_param(GIT_ORGANIZATION_NAME).lower()
    p.parameters["<GIT_ORGANIZATION_NAME>"] = org_name
    p.parameters["<GIT_REPOSITORY_ROOT>"] = f'github.com/{org_name}'
    p.parameters["<DOMAIN_NAME>"] = p.get_input_param(DOMAIN_NAME).lower()
    p.parameters["<KUBECTL_VERSION>"] = KUBECTL_VERSION
    p.parameters["<TERRAFORM_VERSION>"] = TERRAFORM_VERSION

    # set IaC webhook secret
    if "<IAC_PR_AUTOMATION_WEBHOOK_SECRET>" not in p.parameters:
        p.parameters["<IAC_PR_AUTOMATION_WEBHOOK_SECRET>"] = random_string_generator(20)

    # set CD webhook secret
    if "<CD_PUSH_EVENT_WEBHOOK_SECRET>" not in p.parameters:
        p.parameters["<CD_PUSH_EVENT_WEBHOOK_SECRET>"] = random_string_generator(20)

    # Ingress URLs for core components. Note!: URL does not contain protocol
    cluster_fqdn = f'{p.get_input_param(DOMAIN_NAME)}'
    p.parameters["<CC_CLUSTER_FQDN>"] = cluster_fqdn
    p.parameters["<SECRET_MANAGER_INGRESS_URL>"] = f'vault.{cluster_fqdn}'
    p.parameters["<CD_INGRESS_URL>"] = f'argocd.{cluster_fqdn}'
    p.parameters["<CI_INGRESS_URL>"] = f'argo.{cluster_fqdn}'
    p.parameters["<IAC_PR_AUTOMATION_INGRESS_URL>"] = f'atlantis.{cluster_fqdn}'
    p.parameters["<REGISTRY_INGRESS_URL>"] = f'harbor.{cluster_fqdn}'
    p.parameters["<GRAFANA_INGRESS_URL>"] = f'grafana.{cluster_fqdn}'
    p.parameters["<CODE_QUALITY_INGRESS_URL>"] = f'sonarqube.{cluster_fqdn}'
    p.parameters["<PORTAL_INGRESS_URL>"] = f'backstage.{cluster_fqdn}'

    # OIDC config
    sec_man_ing = f'{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}'
    p.parameters["<OIDC_PROVIDER_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx'
    p.parameters["<OIDC_PROVIDER_AUTHORIZE_URL>"] = f'{sec_man_ing}/ui/vault/identity/oidc/provider/cgdevx/authorize'
    p.parameters["<OIDC_PROVIDER_TOKEN_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx/token'
    p.parameters["<OIDC_PROVIDER_USERINFO_URL>"] = f'{sec_man_ing}/v1/identity/oidc/provider/cgdevx/userinfo'
    p.parameters["<CD_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<CD_INGRESS_URL>"]}/auth/callback'
    p.parameters["<CI_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<CI_INGRESS_URL>"]}/oauth2/callback'
    p.parameters["<PORTAL_OAUTH_CALLBACK_URL>"] = f'{p.parameters["<PORTAL_INGRESS_URL>"]}/oauth2/callback'
    p.parameters["<REGISTRY_REGISTRY_URL>"] = f'{p.parameters["<REGISTRY_INGRESS_URL>"]}'
    p.parameters[
        "<IAC_PR_AUTOMATION_WEBHOOK_URL>"] = f'https://{p.parameters["<IAC_PR_AUTOMATION_INGRESS_URL>"]}/events'

    return p


@trace()
def cloud_provider_check(manager: CloudProviderManager, p: StateStore) -> None:
    if not manager.evaluate_permissions():
        raise click.ClickException("Insufficient IAM permission")


@trace()
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


@trace()
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

    if params.get_input_param(OPTIONAL_SERVICES):
        incorrect_services = [v for v in params.get_input_param(OPTIONAL_SERVICES) if not OptionalServices.has_value(v)]
        if incorrect_services:
            click.echo(
                f"Features list parsing error: unsupported features found - {str.join(', ', incorrect_services)}")
            return False

    return True
