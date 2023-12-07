import os
import pathlib
import shutil

import click
from ghrepo import GHRepo
from git import Repo, GitError, Actor

from common.command_utils import str_to_kebab, init_cloud_provider
from common.const.common_path import LOCAL_GITOPS_FOLDER, LOCAL_FOLDER
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from services.template_manager import GitOpsTemplateManager


@click.command()
@click.option('--workload-name', '-w', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-repository-name', '-wrn', 'wl_repo_name', help='Workload repository name', type=click.STRING)
@click.option('--workload-gitops-repository-name', '-wgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING)
@click.option('--workload-template-url', '-wtu', 'wl_template_url', help='Workload repository template',
              type=click.STRING)
@click.option('--workload-template-branch', '-wtb', 'wl_template_branch', help='Workload repository template',
              type=click.STRING)
@click.option('--workload-gitops-template-url', '-wgu', 'wl_gitops_template_url',
              help='Workload GitOps repository template', type=click.STRING)
@click.option('--workload-gitops-template-branch', '-wgb', 'wl_gitops_template_branch',
              help='Workload GitOps repository template',
              type=click.STRING)
@click.option('--workload-service-name', '-ws', 'wl_svc_name', help='Workload service name', type=click.STRING)
@click.option('--workload-service-port', '-wsp', 'wl_svc_port', help='Workload service port', type=click.INT)
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

    if not os.path.exists(LOCAL_FOLDER):
        raise click.ClickException("CG DevX metadata does not exist on this machine")

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

    if not wl_template_branch:
        wl_template_branch = "main"
    if not wl_template_url:
        wl_template_url = "git@github.com:CloudGeometry/cg-devx-wl-template.git"

    if not wl_gitops_template_branch:
        wl_gitops_template_branch = "main"
    if not wl_gitops_template_url:
        wl_gitops_template_url = "git@github.com:CloudGeometry/cg-devx-wl-gitops-template.git"

    if not os.path.exists(LOCAL_GITOPS_FOLDER):
        raise click.ClickException("GitOps repo does not exist")

    temp_folder = LOCAL_FOLDER / ".wl_tmp"

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)

    os.makedirs(temp_folder)

    key_path = p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]

    # workload repo
    wl_repo_folder = temp_folder / wl_repo_name
    os.makedirs(wl_repo_folder)

    try:
        wl_repo = Repo.clone_from(GHRepo(p.parameters["<GIT_ORGANIZATION_NAME>"], wl_repo_name).ssh_url,
                                  wl_repo_folder,
                                  env={"GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {key_path}'})
    except GitError as e:
        raise click.ClickException("Failed cloning repo")

    wl_template_repo_folder = temp_folder / GHRepo.parse(wl_template_url).name
    os.makedirs(wl_template_repo_folder)

    try:
        wl_template_repo = Repo.clone_from(wl_template_url,
                                           wl_template_repo_folder,
                                           branch=wl_template_branch,
                                           env={"GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {key_path}'})
    except GitError as e:
        raise click.ClickException("Failed cloning template repo")

    shutil.rmtree(wl_template_repo_folder / ".git")
    shutil.copytree(wl_template_repo_folder, wl_repo_folder, dirs_exist_ok=True)
    shutil.rmtree(wl_template_repo_folder)
    shutil.move(wl_repo_folder / "wl-service-name", wl_repo_folder / wl_svc_name)

    wl_repo_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
    }
    for root, dirs, files in os.walk(wl_repo_folder):
        for name in files:
            if name.endswith(".tf") or name.endswith(".yaml") or name.endswith(".yml") or name.endswith(".md"):
                file_path = os.path.join(root, name)
                with open(file_path, "r") as file:
                    data = file.read()
                    for k, v in wl_repo_params.items():
                        data = data.replace(k, v)
                with open(file_path, "w") as file:
                    file.write(data)

    wl_repo.git.add(all=True)
    author = Actor(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])
    wl_repo.index.commit("initial", author=author, committer=author)

    wl_repo.remotes.origin.push(wl_repo.active_branch.name)

    # wl gitops repo
    cloud_man, dns_man = init_cloud_provider(p)

    wl_gitops_repo_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<WL_SERVICE_URL>": f'{wl_svc_name}.{wl_name}.{p.parameters["<CC_CLUSTER_FQDN>"]}',
        "<WL_SERVICE_IMAGE>": f'{p.parameters["<REGISTRY_REGISTRY_URL>"]}/{wl_name}/{wl_svc_name}',
        "<WL_SERVICE_PORT>": str(wl_svc_port),
        "# <K8S_ROLE_MAPPING>": cloud_man.create_k8s_cluster_role_mapping_snippet(),
        "<WL_IAM_ROLE_RN>": "[Put your workload service role mapping]",
        "# <ADDITIONAL_LABELS>": cloud_man.create_additional_labels(),
    }

    wl_gitops_repo_folder = temp_folder / wl_gitops_repo_name
    os.makedirs(wl_gitops_repo_folder)

    try:
        wl_gitops_repo = Repo.clone_from(GHRepo(p.parameters["<GIT_ORGANIZATION_NAME>"], wl_gitops_repo_name).ssh_url,
                                         wl_gitops_repo_folder,
                                         env={"GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {key_path}'})
    except GitError as e:
        raise click.ClickException("Failed cloning repo")

    wl_gitops_template_repo_folder = temp_folder / GHRepo.parse(wl_gitops_template_url).name
    os.makedirs(wl_gitops_template_repo_folder)

    try:
        wl_gitops_template_repo = Repo.clone_from(wl_gitops_template_url,
                                                  wl_gitops_template_repo_folder,
                                                  branch=wl_gitops_template_branch,
                                                  env={
                                                      "GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {key_path}'})
    except GitError as e:
        raise click.ClickException("Failed cloning template repo")

    shutil.rmtree(wl_gitops_template_repo_folder / ".git")
    shutil.copytree(wl_gitops_template_repo_folder, wl_gitops_repo_folder, dirs_exist_ok=True)
    shutil.rmtree(wl_gitops_template_repo_folder)

    for root, dirs, files in os.walk(wl_gitops_repo_folder):
        for name in files:
            if name.endswith(".tf") or name.endswith(".yaml") or name.endswith(".yml") or name.endswith(".md"):
                file_path = os.path.join(root, name)
                with open(file_path, "r") as file:
                    data = file.read()
                    for k, v in wl_gitops_repo_params.items():
                        data = data.replace(k, v)
                with open(file_path, "w") as file:
                    file.write(data)

    wl_gitops_repo.git.add(all=True)
    author = Actor(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])
    wl_gitops_repo.index.commit("initial", author=author, committer=author)

    wl_gitops_repo.remotes.origin.push(wl_gitops_repo.active_branch.name)

    # remove temp folder
    shutil.rmtree(temp_folder)

    click.echo("Bootstrapping workload. Done!")
    return True
