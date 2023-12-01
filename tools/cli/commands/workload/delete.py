import json
import os

import click
import requests
from git import Actor, Repo

from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_SECRETS_MANAGER, \
    LOCAL_GITOPS_FOLDER, LOCAL_TF_FOLDER_CORE_SERVICES, LOCAL_FOLDER
from common.logging_config import configure_logging, logger
from common.state_store import StateStore


@click.command()
@click.option('--workload-name', '-w', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def delete(wl_name: str, verbosity: str):
    """Deletes all the workload boilerplate."""

    click.echo("Delete workload GitOps code.")

    # Set up global logger
    configure_logging(verbosity)

    p: StateStore = StateStore()

    if not os.path.exists(LOCAL_GITOPS_FOLDER):
        raise Exception("GitOps repo does not exist")

    # reset & update repo just in case
    repo = Repo(LOCAL_GITOPS_FOLDER)
    main_branch = "main"
    current = repo.create_head(main_branch)
    current.checkout()
    repo.git.reset("--hard")
    origin = repo.remotes.origin
    origin.pull(repo.active_branch)

    # create new branch
    branch_name = f"feature/{wl_name}-destroy"
    current = repo.create_head(branch_name)
    current.checkout()

    # repos
    with open(LOCAL_TF_FOLDER_VCS / "terraform.tfvars.json", "r") as file:
        vcs_tf_vars = json.load(file)

    if wl_name in vcs_tf_vars["workloads"]:
        del vcs_tf_vars["workloads"][wl_name]

    with open(LOCAL_TF_FOLDER_VCS / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(vcs_tf_vars, indent=2))

    # secrets
    with open(LOCAL_TF_FOLDER_SECRETS_MANAGER / "terraform.tfvars.json", "r") as file:
        secrets_tf_vars = json.load(file)

    if wl_name in secrets_tf_vars["workloads"]:
        del secrets_tf_vars["workloads"][wl_name]

    with open(LOCAL_TF_FOLDER_SECRETS_MANAGER / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(secrets_tf_vars, indent=2))

    # core services
    with open(LOCAL_TF_FOLDER_CORE_SERVICES / "terraform.tfvars.json", "r") as file:
        services_tf_vars = json.load(file)

    if wl_name in services_tf_vars["workloads"]:
        del services_tf_vars["workloads"][wl_name]

    with open(LOCAL_TF_FOLDER_CORE_SERVICES / "terraform.tfvars.json", "w") as file:
        file.write(json.dumps(services_tf_vars, indent=2))

    # delete ArgoCD manifest
    os.remove(LOCAL_FOLDER / f"/gitops-pipelines/delivery/clusters/cc-cluster/workload/{wl_name}.yaml")

    # commit and prepare a PR
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
        "title": f"remove {wl_name}",
        "body": "Remove default secrets, user and repository structure.",
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
