import os
import os
import shutil
import webbrowser

import click
from ghrepo import GHRepo
from git import Repo, GitError

from common.command_utils import str_to_kebab, prepare_cloud_provider_auth_env_vars, set_envs, \
    check_installation_presence, init_git_provider
from common.const.common_path import LOCAL_FOLDER
from common.const.parameter_names import GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.logging_config import configure_logging
from common.state_store import StateStore
from services.platform_gitops import PlatformGitOpsRepo
from services.tf_wrapper import TfWrapper


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-gitops-repository-name', '-wlgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING)
@click.option('--destroy-resources', '-wldr', 'destroy_resources', help='Destroy workload resources', is_flag=True,
              default=False)
@click.option('--verbosity', type=click.Choice(
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    case_sensitive=False
), default='CRITICAL', help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def delete(wl_name: str, wl_gitops_repo_name: str, destroy_resources: bool, verbosity: str):
    """Deletes all the workload boilerplate."""
    click.confirm(f'This will delete the workload "{wl_name}". Please confirm to continue', abort=True)

    click.echo("Deleting workload GitOps code...")

    # Set up global logger
    configure_logging(verbosity)

    check_installation_presence()

    wl_name = str_to_kebab(wl_name)

    if not wl_gitops_repo_name:
        wl_gitops_repo_name = f"{wl_name}-gitops"

    wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name)

    p: StateStore = StateStore()
    main_branch = "main"

    git_man = init_git_provider(p)
    gor = PlatformGitOpsRepo(git_man,
                             author_name=p.internals["GIT_USER_NAME"],
                             author_email=p.internals["GIT_USER_EMAIL"],
                             key_path=p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"], )
    # update repo just in case
    gor.update()

    # create new branch
    branch_name = f"feature/{wl_name}-destroy"
    gor.create_branch(branch_name)

    gor.rm_workload(wl_name)

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
            key_path = p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]
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

            if os.path.exists(wl_gitops_repo_folder / "terraform"):
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
    gor.upload_changes()

    try:
        pr_url = gor.create_pr(p.parameters["<GITOPS_REPOSITORY_NAME>"],
                               branch_name, main_branch,
                               f"remove {wl_name}",
                               f"Remove default secrets, user and repository structure.")
        webbrowser.open(pr_url, autoraise=False)
    except Exception as e:
        raise click.ClickException("Could not create PR")

    gor.switch_to_branch()

    click.echo("Deleting workload GitOps code. Done!")
    return True
