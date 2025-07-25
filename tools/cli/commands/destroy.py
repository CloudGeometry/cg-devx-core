import asyncio
import shutil
import time

import click
import urllib3
from git import InvalidGitRepositoryError

from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, LOCAL_FOLDER
from common.const.namespaces import ARGOCD_NAMESPACE
from common.enums.git_providers import GitProviders
from common.logging_config import configure_logging
from common.state_store import StateStore
from common.utils.command_utils import init_cloud_provider, prepare_cloud_provider_auth_env_vars, set_envs, unset_envs, \
    wait, init_git_provider, check_installation_presence, prepare_git_provider_env_vars
from common.utils.k8s_utils import find_pod_by_name_fragment
from services.k8s.delivery_service_manager import DeliveryServiceManager, delete_application_via_k8s_portforward
from services.k8s.k8s import KubeClient
from services.platform_gitops import PlatformGitOpsRepo
from services.tf_wrapper import TfWrapper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command()
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def destroy(verbosity: str):
    """Destroy existing CG DevX installation."""
    # Initialize the start time to measure the duration of the platform destruction
    func_start_time = time.time()

    # Set up global logger
    configure_logging(verbosity)

    check_installation_presence()

    # TODO: check if we could move vcs destroy to the last step

    p: StateStore = StateStore()

    git_man = init_git_provider(p)

    if p.has_checkpoint("gitops-vcs"):
        try:
            gor = PlatformGitOpsRepo(
                git_man=git_man,
                author_name=p.internals["GIT_USER_NAME"],
                author_email=p.internals["GIT_USER_EMAIL"],
                key_path=p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
                repo_remote_url=p.parameters.get("<GIT_REPOSITORY_GIT_URL>")
            )
        except InvalidGitRepositoryError:
            raise click.ClickException("GitOps repo does not exist")

        gor.update()

    click.confirm(
        f'This will destroy cluster "{p.parameters["<PRIMARY_CLUSTER_NAME>"]}" and local files at "{LOCAL_FOLDER}". '
        f'Please confirm to continue', abort=True)

    click.echo("Destroying CG DevX installation...")

    cloud_man, dns_man = init_cloud_provider(p)
    cloud_provider_auth_env_vars = prepare_cloud_provider_auth_env_vars(p)
    git_provider_env_vars = prepare_git_provider_env_vars(p)

    tf_env_vars = {
        **cloud_provider_auth_env_vars,
        **git_provider_env_vars,
        **{
            "VAULT_TOKEN": p.internals.get("VAULT_ROOT_TOKEN", None),
            "VAULT_ADDR": f'https://{p.parameters.get("<SECRET_MANAGER_INGRESS_URL>", None)}',
        }
    }
    # set envs as required by tf
    set_envs(tf_env_vars)

    # ArgoCD section
    # wait till resources are de-provisioned by ArgoCD before destroying K8s cluster
    if p.has_checkpoint("k8s-delivery"):
        click.echo("Deleting ArgoCD configuration...")

        # remove apps with dependencies on external resources
        kube_client = KubeClient(config_file=p.internals["KCTL_CONFIG_PATH"])
        cd_man = DeliveryServiceManager(kube_client)
        # turn off sync
        registry_app_name = "registry"
        try:
            cd_man.turn_off_app_sync(registry_app_name)
            cd_man.turn_off_app_sync("ingress-nginx-components")
            cd_man.turn_off_app_sync("ingress-nginx")
            # git self-hosted runners
            if p.git_provider == GitProviders.GitHub:
                cd_man.turn_off_app_sync("github-runner-components")
                cd_man.turn_off_app_sync("actions-runner-controller-components")
            elif p.git_provider == GitProviders.GitLab:
                cd_man.turn_off_app_sync("gitlab-runner-components")
                cd_man.turn_off_app_sync("gitlab-agent-components")
            else:
                raise Exception('Error: None of the available Git providers were specified')

            # delete apps
            cd_man.delete_app("ingress-nginx-components")
            cd_man.delete_app("ingress-nginx")
            # git self-hosted runners
            if p.git_provider == GitProviders.GitHub:
                cd_man.delete_app("github-runner-components")
                cd_man.delete_app("actions-runner-controller-components")
            elif p.git_provider == GitProviders.GitLab:
                cd_man.delete_app("gitlab-runner-components")
                cd_man.delete_app("gitlab-agent-components")
            else:
                raise Exception('Error: None of the available Git providers were specified')

        except Exception as e:
            pass
        try:
            deletion_wait_time = 300
            k8s_pod = find_pod_by_name_fragment(
                kube_config_path=p.internals["KCTL_CONFIG_PATH"],
                name_fragment="argocd-server",
                namespace=ARGOCD_NAMESPACE
            )
            # Transitioned to asynchronous functions to address compatibility issues with the kr8s library.
            # Previously, the synchronous interaction with kr8s sometimes led to deadlocks and errors because the kr8s
            # library is inherently asynchronous.
            asyncio.run(delete_application_via_k8s_portforward(
                app_name=registry_app_name,
                user=p.internals["ARGOCD_USER"],
                password=p.internals["ARGOCD_PASSWORD"],
                k8s_pod=k8s_pod,
                kube_config_path=p.internals["KCTL_CONFIG_PATH"]
            ))
            click.echo(
                f"Application deletion successfully initiated. "
                f"Waiting {deletion_wait_time} seconds for complete removal."
            )
            # need to wait for application deletion
            wait(deletion_wait_time)
        except Exception as e:
            # suppress exception and continue without deleting ArgoCD app
            pass

        click.echo("Deleting ArgoCD configuration. Done!")

    # K8s Cluster section
    if p.has_checkpoint("k8s-tf"):
        click.echo("Destroying K8s cluster...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_HOSTING_PROVIDER)
        tf_wrapper.init()
        tf_wrapper.destroy({"cluster_ssh_public_key": p.parameters.get("<CC_CLUSTER_SSH_PUBLIC_KEY>", "")})

        click.echo("Destroying K8s cluster. Done!")

    if p.has_checkpoint("vcs-tf"):
        click.echo("Destroying VCS...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.destroy()

        click.echo("Destroying VCS. Done!")

    # unset envs as no longer needed
    unset_envs(tf_env_vars)

    # delete IaC backend storage bucket
    if not cloud_man.destroy_iac_state_storage(p.internals["TF_BACKEND_STORAGE_NAME"]):
        click.echo(f'Failed to delete IaC state storage {p.internals["TF_BACKEND_STORAGE_NAME"]}. You should delete '
                   f'it manually.')

    # delete local data folder
    shutil.rmtree(LOCAL_FOLDER)

    # Calculate the total seconds elapsed
    total_seconds = time.time() - func_start_time

    # Use divmod to separate the total seconds into minutes and seconds
    minutes, seconds = divmod(total_seconds, 60)

    # Display the result with minutes as integers and seconds with two decimal places
    click.echo(f"Platform destroy completed in {int(minutes)} minutes, {int(seconds)} seconds")
