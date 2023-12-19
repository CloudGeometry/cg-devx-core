import os
import shutil

import click
from ghrepo import GHRepo
from git import Repo, GitError, Actor

from common.const.common_path import LOCAL_GITOPS_FOLDER, LOCAL_FOLDER, LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import WL_REPOSITORY_URL, WL_GITOPS_REPOSITORY_URL
from common.logging_config import configure_logging
from common.state_store import StateStore
from common.utils.command_utils import str_to_kebab, init_cloud_provider, check_installation_presence
from services.wl_gitops_template_manager import WorkloadGitOpsTemplateManager
from services.wl_template_manager import WorkloadTemplateManager


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-repository-name', '-wlrn', 'wl_repo_name', help='Workload repository name', type=click.STRING)
@click.option('--workload-gitops-repository-name', '-wlgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING)
@click.option('--workload-template-url', '-wltu', 'wl_template_url', help='Workload repository template',
              type=click.STRING)
@click.option('--workload-template-branch', '-wltb', 'wl_template_branch', help='Workload repository template branch',
              type=click.STRING)
@click.option('--workload-gitops-template-url', '-wlgu', 'wl_gitops_template_url',
              help='Workload GitOps repository template', type=click.STRING)
@click.option('--workload-gitops-template-branch', '-wlgb', 'wl_gitops_template_branch',
              help='Workload GitOps repository template branch',
              type=click.STRING)
@click.option('--workload-service-name', '-wls', 'wl_svc_name', help='Workload service name', type=click.STRING)
@click.option('--workload-service-port', '-wlsp', 'wl_svc_port', help='Workload service port', type=click.INT)
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def bootstrap(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, wl_template_url: str, wl_template_branch: str,
              wl_gitops_template_url: str, wl_gitops_template_branch: str, wl_svc_name: str, wl_svc_port: int,
              verbosity: str):
    """Bootstrap workload repository with template."""
    click.echo("Bootstrapping workload...")
    # Set up global logger
    configure_logging(verbosity)

    check_installation_presence()

    p: StateStore = StateStore()

    wl_name = str_to_kebab(wl_name)

    if not wl_repo_name:
        wl_repo_name = wl_name

    if not wl_gitops_repo_name:
        if wl_repo_name:
            wl_gitops_repo_name = f"{wl_repo_name}-gitops"
        else:
            wl_gitops_repo_name = f"{wl_name}-gitops"

    if not wl_svc_name:
        wl_svc_name = "wl-service"

    if not wl_svc_port:
        wl_svc_port = 3000

    wl_svc_name = str_to_kebab(wl_svc_name)
    wl_repo_name = str_to_kebab(wl_repo_name)
    wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name)

    if os.path.exists(LOCAL_WORKLOAD_TEMP_FOLDER):
        shutil.rmtree(LOCAL_WORKLOAD_TEMP_FOLDER)

    os.makedirs(LOCAL_WORKLOAD_TEMP_FOLDER)

    wl_man = WorkloadTemplateManager(
        org_name=p.parameters["<GIT_ORGANIZATION_NAME>"],
        repo_name=wl_repo_name,
        key_path=p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
        template_url=wl_template_url,
        template_branch=wl_template_branch
    )

    # workload repo
    if not (wl_man.clone_wl()):
        raise click.ClickException("Failed cloning repo")

    if not (wl_man.clone_template()):
        raise click.ClickException("Failed cloning template repo")

    # make wl_svc_name multiple value param
    wl_man.bootstrap([wl_svc_name])

    wl_repo_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
    }

    wl_man.parametrise(wl_repo_params)

    wl_man.upload(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])

    wl_man.cleanup()

    # wl gitops repo
    cloud_man, dns_man = init_cloud_provider(p)
    wl_ops_man = WorkloadGitOpsTemplateManager(
        org_name=p.parameters["<GIT_ORGANIZATION_NAME>"],
        repo_name=wl_gitops_repo_name,
        key_path=p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
        template_url=wl_gitops_template_url,
        template_branch=wl_gitops_template_branch
    )

    # workload repo
    if not (wl_ops_man.clone_wl()):
        raise click.ClickException("Failed cloning repo")

    if not (wl_ops_man.clone_template()):
        raise click.ClickException("Failed cloning template repo")

    wl_ops_man.bootstrap()

    wl_gitops_repo_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<WL_SERVICE_URL>": f'{wl_svc_name}.{wl_name}.{p.parameters["<CC_CLUSTER_FQDN>"]}',
        "<WL_SERVICE_IMAGE>": f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{wl_name}/{wl_svc_name}',
        "<WL_SERVICE_PORT>": str(wl_svc_port),
        "# <K8S_ROLE_MAPPING>": cloud_man.create_k8s_cluster_role_mapping_snippet(),
        "<WL_IAM_ROLE_RN>": "[Put your workload service role mapping]",
        "# <ADDITIONAL_LABELS>": cloud_man.create_additional_labels(),
        "# <TF_WL_SECRETS_REMOTE_BACKEND>": cloud_man.create_iac_backend_snippet(p.internals["TF_BACKEND_STORAGE_NAME"],
                                                                                 f"workloads/{wl_name}/secrets"),
        "# <TF_WL_HOSTING_REMOTE_BACKEND>": cloud_man.create_iac_backend_snippet(p.internals["TF_BACKEND_STORAGE_NAME"],
                                                                                 f"workloads/{wl_name}/hosting_provider"),
        "# <TF_HOSTING_PROVIDER>": cloud_man.create_hosting_provider_snippet(),
    }

    wl_ops_man.parametrise(wl_gitops_repo_params)

    wl_ops_man.upload(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])

    wl_ops_man.cleanup()

    # remove temp folder
    shutil.rmtree(LOCAL_WORKLOAD_TEMP_FOLDER)

    click.echo("Bootstrapping workload. Done!")
    return True
