import os
import os
import os
import shutil
import time

import click
import portforward
import urllib3

from common.command_utils import init_cloud_provider
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, LOCAL_FOLDER
from common.const.namespaces import ARGOCD_NAMESPACE
from common.const.parameter_names import CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, CLOUD_ACCOUNT_ACCESS_SECRET, \
    GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.state_store import StateStore
from services.k8s.delivery_service_manager import DeliveryServiceManager, get_argocd_token, delete_application
from services.k8s.k8s import KubeClient
from services.tf_wrapper import TfWrapper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command()
def destroy():
    """Destroy existing CG DevX installation."""
    click.echo("Destroys CG DevX installation.")
    p: StateStore = StateStore()

    cloud_man, dns_man = init_cloud_provider(p)

    cloud_provider_auth_env_vars = {k: v for k, v in {
        "AWS_PROFILE": p.get_input_param(CLOUD_PROFILE),
        "AWS_ACCESS_KEY_ID": p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
        "AWS_SECRET_ACCESS_KEY": p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET),
        "AWS_DEFAULT_REGION": p.parameters["<CLOUD_REGION>"],
    }.items() if v}

    tf_env_vars = {
        **cloud_provider_auth_env_vars,
        **{
            "GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
            "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME),
            "VAULT_TOKEN": p.internals["VAULT_ROOT_TOKEN"],
            "VAULT_ADDR": f'https://{p.parameters["<SECRET_MANAGER_INGRESS_URL>"]}',
        }
    }
    # set envs as required by tf
    for k, vault_i in tf_env_vars.items():
        os.environ[k] = vault_i

    if p.has_checkpoint("vcs-tf"):
        click.echo("Destroying VCS...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.destroy()

    # if p.has_checkpoint("users-tf"):
    #     click.echo("Destroying VCS...")
    #
    #     tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_USERS)
    #     tf_wrapper.init()
    #     tf_wrapper.destroy()

    # ArgoCD section
    # wait till resources are de-provisioned by ArgoCD before destroying K8s cluster
    if p.has_checkpoint("k8s-delivery"):
        click.echo("Removing ArgoCD configuration...")

    # remove apps with dependencies on external resources
    k8s_token = cloud_man.get_k8s_token(p.parameters["<PRIMARY_CLUSTER_NAME>"])
    kube_client = KubeClient(p.internals["CC_CLUSTER_CA_CERT_PATH"], k8s_token, p.internals["CC_CLUSTER_ENDPOINT"])
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

    # need to wait here
    time.sleep(120)

    with portforward.forward(ARGOCD_NAMESPACE, "argocd-server", 8080, 8080,
                             config_path=p.internals["KCTL_CONFIG_PATH"], waiting=3):

        argocd_token = get_argocd_token(p.internals["ARGOCD_USER"], p.internals["ARGOCD_PASSWORD"])
        delete_application(registry_app_name, argocd_token)

    # need to wait here
    time.sleep(300)

    # K8s Cluster section
    if p.has_checkpoint("k8s-tf"):
        click.echo("Destroying K8s cluster...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_HOSTING_PROVIDER)
        tf_wrapper.init()
        tf_wrapper.destroy()

    # unset envs as no longer needed
    for k in tf_env_vars.keys():
        os.environ.pop(k)

    # delete IaC backend storage bucket
    cloud_man.destroy_iac_state_storage(p.internals["TF_BACKEND_STORAGE_NAME"])

    # delete local data folder
    shutil.rmtree(LOCAL_FOLDER)
    return
