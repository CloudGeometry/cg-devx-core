import json
import os
import shutil

import click
from ghrepo import GHRepo
from git import Repo, GitError, Actor

from common.command_utils import str_to_kebab, update_gitops_repo, prepare_cloud_provider_auth_env_vars, set_envs, \
    create_pr
from common.const.common_path import LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_SECRETS_MANAGER, \
    LOCAL_GITOPS_FOLDER, LOCAL_TF_FOLDER_CORE_SERVICES, LOCAL_FOLDER, LOCAL_CC_CLUSTER_WORKLOAD_FOLDER
from common.const.parameter_names import GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.logging_config import configure_logging
from common.state_store import StateStore
from services.tf_wrapper import TfWrapper


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-gitops-repository-name', '-wlgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING)
@click.option('--destroy-resources', '-wldr', 'destroy_resources', help='Destroy workload resources', is_flag=True, default=False)
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def delete(wl_name: str, wl_gitops_repo_name: str, destroy_resources: bool, verbosity: str):
    """Deletes all the workload boilerplate."""
    click.confirm("This will delete workload. Please confirm to continue", abort=True)

    click.echo("Deleting workload GitOps code...")

    # Set up global logger
    configure_logging(verbosity)

    if not os.path.exists(LOCAL_FOLDER):
        raise click.ClickException("CG DevX metadata does not exist on this machine")

    p: StateStore = StateStore()

    wl_name = str_to_kebab(wl_name)

    if not wl_gitops_repo_name:
        wl_gitops_repo_name = f"{wl_name}-gitops"

    wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name)

    if not os.path.exists(LOCAL_GITOPS_FOLDER):
        raise click.ClickException("GitOps repo does not exist")

    main_branch = "main"

    repo = update_gitops_repo()

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
    wl_argo_manifest = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / f"{wl_name}.yaml"
    if os.path.exists(wl_argo_manifest):
        os.remove(wl_argo_manifest)

    key_path = p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]

    # destroy resources
    if destroy_resources:
        # to destroy workload resources, we need to clone workload gitops repo
        # and call tf destroy while pointing to remote state
        tf_destroy_confirmation: bool = click.confirm(
            "This will delete all the resources defined in workload IaC. Please confirm to continue")

        if tf_destroy_confirmation:
            temp_folder = LOCAL_FOLDER / ".wl_tmp"
            wl_gitops_repo_folder = temp_folder / f"{wl_name}-gitops"

            if os.path.exists(wl_gitops_repo_folder):
                shutil.rmtree(wl_gitops_repo_folder)

            os.makedirs(wl_gitops_repo_folder)

            try:
                wl_gitops_repo = Repo.clone_from(
                    GHRepo(p.parameters["<GIT_ORGANIZATION_NAME>"], wl_gitops_repo_name).ssh_url,
                    wl_gitops_repo_folder,
                    env={"GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {key_path}'})
            except GitError as e:
                raise click.ClickException("Failed cloning repo")

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

            click.echo("Destroying WL secrets...")

            tf_wrapper = TfWrapper(wl_gitops_repo_folder / "terraform/secrets")
            tf_wrapper.init()
            tf_wrapper.destroy()

            click.echo("Destroying WL secrets. Done!")

            click.echo("Destroying WL cloud resources...")

            tf_wrapper = TfWrapper(wl_gitops_repo_folder / "terraform/infrastructure")
            tf_wrapper.init()
            tf_wrapper.destroy()

            click.echo("Destroying WL cloud resources. Done!")

            # remove temp folder
            shutil.rmtree(temp_folder)

    # commit and prepare a PR
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {key_path}'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):

        repo.git.add(all=True)
        author = Actor(name=p.internals["GIT_USER_NAME"], email=p.internals["GIT_USER_EMAIL"])
        repo.index.commit("initial", author=author, committer=author)

        repo.remotes.origin.push(repo.active_branch.name)

    if not create_pr(p.parameters["<GIT_ORGANIZATION_NAME>"], p.parameters["<GITOPS_REPOSITORY_NAME>"],
                     p.internals["GIT_ACCESS_TOKEN"],
                     branch_name, main_branch,
                     f"remove {wl_name}",
                     f"Remove default secrets, user and repository structure."):
        raise click.ClickException("Could not create PR")

    repo.heads.main.checkout()

    click.echo("Deleting workload GitOps code. Done!")
    return True
