import shutil
import time

import click
import urllib3
from git import InvalidGitRepositoryError

from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, LOCAL_FOLDER
from common.const.namespaces import ARGOCD_NAMESPACE
from common.logging_config import configure_logging
from common.state_store import StateStore
from common.utils.command_utils import init_cloud_provider, prepare_cloud_provider_auth_env_vars, set_envs, unset_envs, \
    wait, init_git_provider, check_installation_presence, prepare_git_provider_env_vars
from common.utils.k8s_utils import get_kr8s_pod_instance_by_name, find_pod_by_name_fragment
from services.k8s.delivery_service_manager import DeliveryServiceManager, get_argocd_token, delete_application
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
            cd_man.turn_off_app_sync("github-runner-components")
            cd_man.turn_off_app_sync("actions-runner-controller-components")

            # delete app
            cd_man.delete_app("ingress-nginx-components")
            cd_man.delete_app("ingress-nginx")
            cd_man.delete_app("github-runner-components")
            cd_man.delete_app("actions-runner-controller-components")
        except Exception as e:
            pass
        try:
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
                argocd_token = get_argocd_token(p.internals["ARGOCD_USER"], p.internals["ARGOCD_PASSWORD"])
                delete_application(registry_app_name, argocd_token)

            # need to wait here
            wait(300)
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
