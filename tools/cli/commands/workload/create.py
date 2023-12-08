import json
import os

import click
from ghrepo import GHRepo
from git import Actor

from common.command_utils import str_to_kebab, update_gitops_repo, create_pr
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_SECRETS_MANAGER, \
    LOCAL_GITOPS_FOLDER, LOCAL_TF_FOLDER_CORE_SERVICES, LOCAL_FOLDER, LOCAL_CC_CLUSTER_WORKLOAD_FOLDER
from common.logging_config import configure_logging
from common.state_store import StateStore


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-repository-name', '-wlrn', 'wl_repo_name', help='Workload repository name',
              type=click.STRING)
@click.option('--workload-gitops-repository-name', '-wlgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING)
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def create(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, verbosity: str):
    """Create workload boilerplate."""
    click.echo("Creating workload GitOps code...")

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

    wl_repo_name = str_to_kebab(wl_repo_name)
    wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name)

    if not os.path.exists(LOCAL_GITOPS_FOLDER):
        raise click.ClickException("GitOps repo does not exist")

    main_branch = "main"

    repo = update_gitops_repo()

    # create new branch
    branch_name = f"feature/{wl_name}-init"
    current = repo.create_head(branch_name)
    current.checkout()

    # repos
    with open(LOCAL_TF_FOLDER_VCS / "terraform.tfvars.json", "r") as file:
        vcs_tf_vars = json.load(file)

    vcs_tf_vars["workloads"][wl_name] = {
        "description": f"CG DevX {wl_name} workload definition",
        "repos": {}
    }
    vcs_tf_vars["workloads"][wl_name]["repos"][wl_repo_name] = {}
    vcs_tf_vars["workloads"][wl_name]["repos"][wl_gitops_repo_name] = {
        "atlantis_enabled": True,
    }
    with open(LOCAL_TF_FOLDER_VCS / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(vcs_tf_vars, indent=2))

    # secrets
    with open(LOCAL_TF_FOLDER_SECRETS_MANAGER / "terraform.tfvars.json", "r") as file:
        secrets_tf_vars = json.load(file)

    secrets_tf_vars["workloads"][wl_name] = {}

    with open(LOCAL_TF_FOLDER_SECRETS_MANAGER / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(secrets_tf_vars, indent=2))

    # core services
    with open(LOCAL_TF_FOLDER_CORE_SERVICES / "terraform.tfvars.json", "r") as file:
        services_tf_vars = json.load(file)

    services_tf_vars["workloads"][wl_name] = {}

    with open(LOCAL_TF_FOLDER_CORE_SERVICES / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(services_tf_vars, indent=2))

    # prepare ArgoCD manifest
    wl_gitops_repo = GHRepo(p.parameters["<GIT_ORGANIZATION_NAME>"], wl_gitops_repo_name)
    params = {
        "<WL_NAME>": wl_name,
        "<WL_GITOPS_REPOSITORY_GIT_URL>": wl_gitops_repo.ssh_url,
    }

    workload_template_file = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / "workload-template.yaml"
    with open(workload_template_file, "r") as file:
        data = file.read()
        for k, v in params.items():
            data = data.replace(k, v)

    workload_file = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / f"{wl_name}.yaml"
    with open(workload_file, "w") as file:
        file.write(data)

    # commit and prepare a PR
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]}'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):

        repo.git.add(all=True)
        author = Actor(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])
        repo.index.commit("initial", author=author, committer=author)

        repo.remotes.origin.push(repo.active_branch.name)

    if not create_pr(p.parameters["<GIT_ORGANIZATION_NAME>"], p.parameters["<GITOPS_REPOSITORY_NAME>"],
                     p.internals["GIT_ACCESS_TOKEN"],
                     branch_name, main_branch,
                     f"introduce {wl_name}",
                     f"Add default secrets, user and default repository structure."):
        raise click.ClickException("Could not create PR")

    repo.heads.main.checkout()

    click.echo("Creating workload GitOps code. Done!")
    return True
