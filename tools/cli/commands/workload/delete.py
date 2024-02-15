import os
import shutil
import time

import click
from git import InvalidGitRepositoryError

from common.const.common_path import LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import GITOPS_REPOSITORY_MAIN_BRANCH, WL_PR_BRANCH_NAME_PREFIX, WL_GITOPS_REPOSITORY_BRANCH, \
    WL_GITOPS_REPOSITORY_URL
from common.const.parameter_names import GIT_ACCESS_TOKEN, GIT_ORGANIZATION_NAME
from common.custom_excpetions import GitBranchAlreadyExists, PullRequestCreationError
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import str_to_kebab, prepare_cloud_provider_auth_env_vars, set_envs, \
    check_installation_presence, initialize_gitops_repository, create_and_setup_branch, \
    create_and_open_pull_request, preprocess_workload_names
from services.platform_gitops import PlatformGitOpsRepo
from services.tf_wrapper import TfWrapper
from services.wl_template_manager import WorkloadManager


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
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
    '--workload-gitops-template-url',
    '-wlgu',
    'wl_gitops_template_url',
    help='Workload GitOps repository template',
    type=click.STRING,
    default=WL_GITOPS_REPOSITORY_URL
)
@click.option(
    '--workload-gitops-template-branch',
    '-wlgb',
    'wl_gitops_template_branch',
    help='Workload GitOps repository template branch',
    type=click.STRING,
    default=WL_GITOPS_REPOSITORY_BRANCH
)
@click.option(
    '--verbosity',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
    default='CRITICAL',
    help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
)
def delete(
        wl_name: str, wl_gitops_repo_name: str, destroy_resources: bool, wl_gitops_template_url: str,
        wl_gitops_template_branch: str, verbosity: str
):
    """
    Deletes all the workload boilerplate, including optionally destroying associated resources.

    This command performs a series of steps to remove a workload and its configurations from the GitOps repository.
    It optionally destroys the resources defined in the workload's Infrastructure as Code (IaC).

    Args:
        wl_name (str): Name of the workload to be deleted.
        wl_gitops_repo_name (str): Name of the GitOps repository associated with the workload.
        destroy_resources (bool): Flag indicating whether to destroy resources defined in the workload's IaC.
        wl_gitops_template_url (str): URL of the GitOps repository template.
        wl_gitops_template_branch (str): Branch of the GitOps repository template.
        main_branch (str): Main branch name of the GitOps repository.
        verbosity (str): Logging level.

    Raises:
        click.ClickException: If any error occurs during the deletion process.
    """
    click.confirm(f'This will delete the workload "{wl_name}". Please confirm to continue', abort=True)
    destroy_resources = destroy_resources and click.confirm(
        "This will delete all the resources defined in workload IaC. Please confirm to continue"
    )
    # Determine the total number of steps
    logging_total_steps = 7 if destroy_resources else 6
    func_start_time = time.time()

    branch_name = f"{WL_PR_BRANCH_NAME_PREFIX}{wl_name}-destroy"
    click.echo("Initializing workload deletion process...")
    state_store: StateStore = StateStore()
    click.echo(f"1/{logging_total_steps}: State store initialized.")

    # Set up global logger
    configure_logging(verbosity=verbosity)
    check_installation_presence()
    click.echo(f"2/{logging_total_steps}: Logging and installation checked.")

    wl_name, wl_repo_name, wl_gitops_repo_name = preprocess_workload_names(
        logger=logger,
        wl_name=wl_name,
        wl_gitops_repo_name=wl_gitops_repo_name,
    )
    click.echo(f"3/{logging_total_steps}: Workload names processed.")
    try:
        git_man, gor = initialize_gitops_repository(state_store=state_store, logger=logger)
    except InvalidGitRepositoryError:
        raise click.ClickException("GitOps repo does not exist")
    click.echo(f"4/{logging_total_steps}: GitOps repository initialized.")

    try:
        create_and_setup_branch(gor=gor, branch_name=branch_name, logger=logger)
    except GitBranchAlreadyExists as e:
        raise click.ClickException(str(e))

    # Optionally destroy resources
    if destroy_resources:
        # to destroy workload resources, we need to clone workload gitops repo
        # and call tf destroy while pointing to remote state
        wl_gitops_manager = WorkloadManager(
            org_name=state_store.parameters["<GIT_ORGANIZATION_NAME>"],
            repo_name=wl_gitops_repo_name,
            key_path=state_store.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
            template_url=wl_gitops_template_url,
            template_branch=wl_gitops_template_branch
        )

        wl_gitops_repo_folder = wl_gitops_manager.clone_wl()

        _set_tf_env_vars_for_tf(state_store=state_store)

        destroy_all_tf_resources(repo_folder=wl_gitops_repo_folder)

        # remove temp folder
        shutil.rmtree(LOCAL_WORKLOAD_TEMP_FOLDER)

        click.echo(f"5/{logging_total_steps}: Workload resources destroyed.")

    _remove_workload_and_commit(wl_name=wl_name, gor=gor)
    click.echo(f"{6 if destroy_resources else 5}/{logging_total_steps}: Workload removed and changes committed.")
    try:
        create_and_open_pull_request(
            gor=gor,
            state_store=state_store,
            title=f"Remove {wl_name}",
            body="Remove default secrets, groups and repository structure.",
            branch_name=branch_name,
            main_branch=GITOPS_REPOSITORY_MAIN_BRANCH,
            logger=logger
        )
    except PullRequestCreationError as e:
        raise click.ClickException(str(e))

    click.echo(f"{7 if destroy_resources else 6}/{logging_total_steps}: Pull request created and opened.")

    gor.switch_to_branch()
    gor.delete_branch(branch_name)

    click.echo(f"Deleting workload GitOps code completed in {time.time() - func_start_time:.2f} seconds.")


def _remove_workload_and_commit(gor: PlatformGitOpsRepo, wl_name: str) -> None:
    """
    Remove the workload to the GitOps repository and commit changes.

    Parameters:
        gor: PlatformGitOpsRepo class instance.
        wl_name (str): Name of the workload.
    """
    gor.rm_workload(wl_name=wl_name)
    gor.upload_changes()
    logger.info("Workload added and committed to the repository.")


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
