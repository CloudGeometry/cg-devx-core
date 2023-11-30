import json
import os

import click
import requests
from git import Actor, Repo

from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_SECRETS_MANAGER, \
    LOCAL_GITOPS_FOLDER, LOCAL_TF_FOLDER_CORE_SERVICES
from common.state_store import StateStore
from common.logging_config import configure_logging, logger


@click.command()
@click.option('--workload-name', '-w', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-repository-name', '-wrn', 'wl_repo_name', help='Workload repository name',
              type=click.STRING)
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
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def create(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, wl_template_url: str, wl_template_branch: str,
           wl_gitops_template_url: str, wl_gitops_template_branch: str, verbosity: str):
    """Create workload boilerplate."""
    click.echo("Create workload.")

    # Set up global logger
    configure_logging(verbosity)

    p: StateStore = StateStore()

    if not os.path.exists(LOCAL_GITOPS_FOLDER):
        raise Exception("GitOps repo does not exist")

    # reset & update repo just in case
    repo = Repo(LOCAL_GITOPS_FOLDER)
    main_branch = repo.active_branch.name
    repo.git.reset("--hard")
    origin = repo.remotes.origin
    origin.pull(repo.active_branch)

    # create new branch
    branch_name = f"feature/{wl_name}-init"
    current = repo.create_head(branch_name)
    current.checkout()

    if not wl_repo_name:
        wl_repo_name = wl_name

    if not wl_gitops_repo_name:
        if wl_repo_name:
            wl_gitops_repo_name = f"{wl_repo_name}-gitops"
        else:
            wl_gitops_repo_name = f"{wl_name}-gitops"

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
        secrets_tf_vars = json.load(file)

    secrets_tf_vars["workloads"][wl_name] = {}

    with open(LOCAL_TF_FOLDER_CORE_SERVICES / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(secrets_tf_vars, indent=2))

    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]}'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):

        repo.git.add(all=True)
        author = Actor(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])
        repo.index.commit("initial", author=author, committer=author)

        repo.remotes.origin.push(repo.active_branch.name)

    git_pulls_api = "https://api.github.com/repos/{0}/{1}/pulls".format(
        p.parameters["<GIT_ORGANIZATION_NAME>"],
        p.parameters["<GITOPS_REPOSITORY_NAME>"]
    )
    headers = {
        "Authorization": "token {0}".format(p.internals["GIT_ACCESS_TOKEN"]),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "title": f"introduce {wl_name}",
        "body": "Add default secrets, user and default repository structure. ",
        "head": branch_name,
        "base": main_branch
    }

    r = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload))

    if not r.ok:
        raise click.ClickException("Could not create PR")
        logger.error("GitHub API Request Failed: {0}".format(r.text))
