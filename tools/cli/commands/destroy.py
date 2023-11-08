import os
import shutil

import click
import portforward
import urllib3

from common.command_utils import init_cloud_provider, prepare_cloud_provider_auth_env_vars, set_envs, unset_envs, wait
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, LOCAL_FOLDER, \
    LOCAL_STATE_FILE
from common.const.namespaces import ARGOCD_NAMESPACE
from common.const.parameter_names import GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.logging_config import configure_logging
from common.state_store import StateStore
from services.k8s.delivery_service_manager import DeliveryServiceManager, get_argocd_token, delete_application
from services.k8s.k8s import KubeClient
from services.tf_wrapper import TfWrapper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command()
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def destroy(verbosity: str):
    """Destroy existing CG DevX installation."""
    # Set up global logger
    configure_logging(verbosity)

    if not os.path.exists(LOCAL_STATE_FILE):
        click.echo("CG DevX installation local files not found.")
        return

    click.echo("Destroying CG DevX installation...")
    p: StateStore = StateStore()

    cloud_man, dns_man = init_cloud_provider(p)
    cloud_provider_auth_env_vars = prepare_cloud_provider_auth_env_vars(p)

    tf_env_vars = {
        **cloud_provider_auth_env_vars,
        **{
            "GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
            "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME),
            "VAULT_TOKEN": p.internals.get("VAULT_ROOT_TOKEN", None),
            "VAULT_ADDR": f'https://{p.parameters.get("<SECRET_MANAGER_INGRESS_URL>", None)}',
        }
    }
    # set envs as required by tf
    set_envs(tf_env_vars)

    if p.has_checkpoint("vcs-tf"):
        click.echo("Destroying VCS...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.destroy()

        click.echo("Destroying VCS. Done!")

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

            # delete app
            cd_man.delete_app("ingress-nginx-components")
            cd_man.delete_app("ingress-nginx")
        except Exception as e:
            pass

        try:
            with portforward.forward(ARGOCD_NAMESPACE, "argocd-server", 8080, 8080,
                                     config_path=p.internals["KCTL_CONFIG_PATH"], waiting=3,
                                     log_level=portforward.LogLevel.ERROR):

                argocd_token = get_argocd_token(p.internals["ARGOCD_USER"], p.internals["ARGOCD_PASSWORD"])
                delete_application(registry_app_name, argocd_token)

            # need to wait here
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
        tf_wrapper.destroy({"ssh_public_key": p.parameters.get("<CC_CLUSTER_SSH_PUBLIC_KEY>", "")})

        click.echo("Destroying K8s cluster. Done!")

    # unset envs as no longer needed
    unset_envs(tf_env_vars)

    # delete IaC backend storage bucket
    cloud_man.destroy_iac_state_storage(p.internals["TF_BACKEND_STORAGE_NAME"])

    # delete local data folder
    shutil.rmtree(LOCAL_FOLDER)

    click.echo("Done!")

    return
