import os
import shutil
import time
from datetime import datetime
from typing import List

import click
from git import InvalidGitRepositoryError

from common.const.common_path import LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import GITOPS_REPOSITORY_MAIN_BRANCH, WL_PR_BRANCH_NAME_PREFIX
from common.const.parameter_names import GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.custom_excpetions import GitBranchAlreadyExists, PullRequestCreationError
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import prepare_cloud_provider_auth_env_vars, set_envs, \
    check_installation_presence, initialize_gitops_repository, create_and_setup_branch, \
    create_and_open_pull_request, preprocess_workload_names
from services.platform_gitops import PlatformGitOpsRepo
from services.tf_wrapper import TfWrapper
from services.wl_template_manager import WorkloadManager


@click.command()
@click.option(
    '--workload-names',
    '-wl',
    'wl_names',
    help='Workload names',
    type=click.STRING,
    multiple=True
)
@click.option(
    '--all',
    'delete_all',
    is_flag=True,
    help='Delete all workloads',
    default=False
)
@click.option(
    '--workload-gitops-repository-name',
    '-wlgrn',
    'wl_gitops_repo_name',
    help='Workload GitOps repository name',
    type=click.STRING
)
@click.option(
    '--destroy-resources',
    '-wldr',
    'destroy_resources',
    help='Destroy workload resources',
    is_flag=True,
    default=False
)
@click.option(
    '--verbosity',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
    default='CRITICAL',
    help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
)
def delete(
        wl_names: List[str],
        delete_all: bool,
        wl_gitops_repo_name: str,
        destroy_resources: bool,
        verbosity: str
):
    """
    Deletes all the workload boilerplate, including optionally destroying associated resources.

    This command performs a series of steps to remove a workload and its configurations from the GitOps repository.
    It optionally destroys the resources defined in the workload's Infrastructure as Code (IaC).

    Args:
        wl_names (List[str]): Names of the workloads to be deleted. Ignored if delete_all is True
        delete_all (bool): If set to True, all workloads will be deleted, ignoring wl_names.
        wl_gitops_repo_name (str): Name of the GitOps repository associated with the workload.
        destroy_resources (bool): Flag indicating whether to destroy resources defined in the workload's IaC.
        verbosity (str): Logging level.

    Raises:
        click.ClickException: If any error occurs during the deletion process.
    """
    # Set up global logger
    configure_logging(verbosity=verbosity)

    state_store: StateStore = StateStore()

    try:
        git_man, gor = initialize_gitops_repository(state_store=state_store, logger=logger)
    except InvalidGitRepositoryError:
        raise click.ClickException("GitOps repo does not exist")
    click.echo(f"GitOps repository initialized.")

    if delete_all:
        wl_names = gor.list_workloads()
    if len(wl_names) == 0:
        raise click.ClickException("There are no workloads to be deleted")

    click.confirm(f"This will delete the workloads \"{', '.join(wl_names)}\". Please confirm to continue", abort=True)
    destroy_resources = destroy_resources and click.confirm(
        "This will delete all the resources defined in workloads IaC. Please confirm to continue"
    )

    # Determine the total number of steps
    logging_total_steps = 6 if destroy_resources else 5
    func_start_time = time.time()

    branch_name = _generate_destroy_branch_name()
    click.echo("Initializing workload deletion process...")

    click.echo(f"1/{logging_total_steps}: State store initialized.")

    check_installation_presence()
    click.echo(f"2/{logging_total_steps}: Logging and installation checked.")

    try:
        create_and_setup_branch(gor=gor, branch_name=branch_name, logger=logger)
    except GitBranchAlreadyExists as e:
        raise click.ClickException(str(e))

    for index, wl_name in enumerate(wl_names):
        wl_name, wl_repo_name, wl_gitops_repo_name = preprocess_workload_names(
            logger=logger,
            wl_name=wl_name,
            wl_gitops_repo_name=wl_gitops_repo_name,
        )
        click.echo(f"3.{index}/{logging_total_steps}: Workload names processed.")

        # Optionally destroy resources
        if destroy_resources:
            # to destroy workload resources, we need to clone workload gitops repo
            # and call tf destroy while pointing to remote state
            wl_gitops_manager = WorkloadManager(
                org_name=state_store.parameters["<GIT_ORGANIZATION_NAME>"],
                wl_repo_name=wl_gitops_repo_name,
                ssh_pkey_path=state_store.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
            )

            wl_gitops_repo_folder = wl_gitops_manager.clone_wl()

            _set_tf_env_vars_for_tf(state_store=state_store)

            destroy_all_tf_resources(repo_folder=wl_gitops_repo_folder)

            # remove temp folder
            shutil.rmtree(LOCAL_WORKLOAD_TEMP_FOLDER)

            click.echo(f"4.{index}/{logging_total_steps}: Workload \"{wl_name}\" resources destroyed.")

        commit_message = f"Remove secrets, groups, repository structure for workload \"{wl_name}\""
        _remove_workload_and_commit(wl_name=wl_name, gor=gor, commit_message=commit_message)
        click.echo(
            f"{5 if destroy_resources else 4}.{index}/{logging_total_steps}: "
            f"Workload \"{wl_name}\" removed and changes committed."
        )

    try:
        create_and_open_pull_request(
            gor=gor,
            state_store=state_store,
            title=f"Remove {wl_names}",
            body="Remove default secrets, groups and repository structure.",
            branch_name=branch_name,
            main_branch=GITOPS_REPOSITORY_MAIN_BRANCH,
            logger=logger
        )
    except PullRequestCreationError as e:
        raise click.ClickException(str(e))

    click.echo(f"{6 if destroy_resources else 5}/{logging_total_steps}: Pull request created and opened.")

    gor.switch_to_branch()
    gor.delete_branch(branch_name)

    click.echo(f"Deleting workloads GitOps code completed in {time.time() - func_start_time:.2f} seconds.")


def _remove_workload_and_commit(gor: PlatformGitOpsRepo, wl_name: str, commit_message: str) -> None:
    """
    Remove the workload from the GitOps repository and commit the changes.

    Parameters:
        gor (PlatformGitOpsRepo): An instance of the PlatformGitOpsRepo class.
        wl_name (str): The name of the workload to be removed.
        commit_message (str): The commit message to be used when committing the changes to the repository.

    The function removes the specified workload and commits the changes with the provided commit message.
    """
    gor.rm_workload(wl_name=wl_name)
    gor.upload_changes(commit_message)
    logger.info(f"Workload removed and committed to the repository with message: {commit_message}")


def _set_tf_env_vars_for_tf(state_store: StateStore) -> None:
    """
    Set environment variables required for Terraform operations.

    Args:
        state_store (StateStore): State store instance for accessing configuration.
    """
    cloud_provider_auth_env_vars = prepare_cloud_provider_auth_env_vars(state_store)
    tf_env_vars = {
        **cloud_provider_auth_env_vars,
        **{
            "GITHUB_TOKEN": state_store.get_input_param(GIT_ACCESS_TOKEN),
            "GITHUB_OWNER": state_store.get_input_param(GIT_ORGANIZATION_NAME),
            "VAULT_TOKEN": state_store.internals.get("VAULT_ROOT_TOKEN", None),
            "VAULT_ADDR": f'https://{state_store.parameters.get("<SECRET_MANAGER_INGRESS_URL>", None)}',
        }
    }
    set_envs(tf_env_vars)


def _destroy_tf_resources(tf_directory: str, resource_description: str) -> None:
    """
    Destroy Terraform resources in the specified directory.

    Args:
        tf_directory (str): Path to the Terraform directory containing configurations to be destroyed.
        resource_description (str): Description of the resources being destroyed (e.g., 'WL secrets', 'WL cloud resources').
    """
    if os.path.exists(tf_directory):
        logger.debug(f"Destroying {resource_description}...")
        tf_wrapper = TfWrapper(tf_directory)
        tf_wrapper.init()
        tf_wrapper.destroy()
        logger.info(f"Destroying {resource_description}. Done!")


def destroy_all_tf_resources(repo_folder: str) -> None:
    """
    Destroy all Terraform resources related to the workload in the specified repository folder.

    Args:
        repo_folder (str): Path to the repository folder containing Terraform configurations.
    """
    _destroy_tf_resources(
        tf_directory=os.path.join(repo_folder, "terraform", "secrets"),
        resource_description="WL secrets"
    )
    _destroy_tf_resources(
        tf_directory=os.path.join(repo_folder, "terraform", "infrastructure"),
        resource_description="WL cloud resources"
    )


def _generate_destroy_branch_name(
        git_folder_prefix: str = WL_PR_BRANCH_NAME_PREFIX, wl_destroy_prefix: str = "workload_destroy_"
) -> str:
    """
    Generate a unique branch name for destroying workloads, incorporating the current date and time.

    Parameters:
        git_folder_prefix (str): The prefix to use for the branch name, which is related to the git folder, defaulting
        to WL_PR_BRANCH_NAME_PREFIX.
        wl_destroy_prefix (str): The prefix to add before "destroy" and the timestamp, defaulting to "workload_destroy_"

    Returns:
        str: The generated branch name, which concatenates the git folder prefix, workload destroy prefix,
        and the current date and time.

    This function constructs a branch name intended to be unique and descriptive, facilitating the identification of
    the branch's purpose and the time of its creation.
    """
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"{git_folder_prefix}{wl_destroy_prefix}{current_time}"

    logger.info(f"Generated branch name: {branch_name}")

    return branch_name
