import os
import shutil

import click

from cli.common.command_utils import init_cloud_provider
from cli.common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_HOSTING_PROVIDER, LOCAL_FOLDER
from cli.common.const.parameter_names import CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, CLOUD_ACCOUNT_ACCESS_SECRET, \
    GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from cli.common.state_store import StateStore
from cli.services.tf_wrapper import TfWrapper


@click.command()
def destroy():
    """Destroy existing CG DevX installation."""
    click.echo("Destroys CG DevX installation.")
    p: StateStore = StateStore()

    cm, dm = init_cloud_provider(p)

    cloud_provider_auth_env_vars = {k: v for k, v in {
        "AWS_PROFILE": p.get_input_param(CLOUD_PROFILE),
        "AWS_ACCESS_KEY_ID": p.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
        "AWS_SECRET_ACCESS_KEY": p.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET),
        "AWS_DEFAULT_REGION": p.parameters["<CLOUD_REGION>"],
    }.items() if v}

    tf_env_vars = cloud_provider_auth_env_vars | {"GITHUB_TOKEN": p.get_input_param(GIT_ACCESS_TOKEN),
                                                  "GITHUB_OWNER": p.get_input_param(GIT_ORGANIZATION_NAME)}
    # set envs as required by tf
    for k, vault_i in tf_env_vars.items():
        os.environ[k] = vault_i

    # K8s Cluster section
    if p.has_checkpoint("k8s-tf"):
        click.echo("Destroying K8s cluster...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_HOSTING_PROVIDER)
        tf_wrapper.init()
        tf_wrapper.destroy()

    if p.has_checkpoint("vcs-tf"):
        click.echo("Destroying VCS...")

        tf_wrapper = TfWrapper(LOCAL_TF_FOLDER_VCS)
        tf_wrapper.init()
        tf_wrapper.destroy()

    # unset envs as no longer needed
    for k in tf_env_vars.keys():
        os.environ.pop(k)

    cm.destroy_iac_state_storage(p.internals["TF_BACKEND_STORAGE_NAME"])

    shutil.rmtree(LOCAL_FOLDER)
