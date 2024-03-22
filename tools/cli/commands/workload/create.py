import time

import click
from git import InvalidGitRepositoryError

from common.const.const import GITOPS_REPOSITORY_MAIN_BRANCH, WL_PR_BRANCH_NAME_PREFIX
from common.custom_excpetions import GitBranchAlreadyExists, PullRequestCreationError
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import check_installation_presence, \
    initialize_gitops_repository, create_and_setup_branch, create_and_open_pull_request, preprocess_workload_names
from services.platform_gitops import PlatformGitOpsRepo


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option(
    '--workload-repository-name',
    '-wlrn',
    'wl_repo_name',
    help='Workload repository name',
    type=click.STRING
)
@click.option(
    '--workload-gitops-repository-name',
    '-wlgrn',
    'wl_gitops_repo_name',
    help='Workload GitOps repository name', type=click.STRING
)
@click.option(
    '--verbosity',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
    default='CRITICAL',
    help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
)
def create(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, verbosity: str) -> None:
    """
    Create workload boilerplate for GitOps.

    Parameters:
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.
        verbosity (str): Logging level.
    """
    func_start_time = time.time()
    click.echo("Initializing workload GitOps code creation...")
    branch_name = f"{WL_PR_BRANCH_NAME_PREFIX}{wl_name}-init"

    configure_logging(verbosity)
    check_installation_presence()

    state_store = StateStore()
    click.echo("1/7: State store initialized.")

    wl_name, wl_repo_name, wl_gitops_repo_name = preprocess_workload_names(
        logger=logger,
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("2/7: Workload names processed.")
    try:
        git_man, gor = initialize_gitops_repository(state_store=state_store, logger=logger)
    except InvalidGitRepositoryError:
        raise click.ClickException("GitOps repo does not exist")
    click.echo("3/7: GitOps repository initialized.")

    try:
        create_and_setup_branch(gor=gor, branch_name=branch_name, logger=logger)
    except GitBranchAlreadyExists as e:
        raise click.ClickException(str(e))

    click.echo(f"4/7: Branch '{branch_name}' created and set up.")

    add_workload_and_commit(
        gor=gor,
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("5/7: Workload added and changes committed.")

    try:
        create_and_open_pull_request(
            gor=gor,
            state_store=state_store,
            title=f"Introduce {wl_name}",
            body="Add default secrets, groups and default repository structure.",
            branch_name=branch_name,
            main_branch=GITOPS_REPOSITORY_MAIN_BRANCH,
            logger=logger
        )
    except PullRequestCreationError as e:
        raise click.ClickException(str(e))

    click.echo(f"6/7: Pull request for branch '{branch_name}' created and opened in the web browser.")

    gor.switch_to_branch(branch_name=GITOPS_REPOSITORY_MAIN_BRANCH)
    gor.delete_branch(branch_name)
    click.echo(f"7/7: Switched to branch '{GITOPS_REPOSITORY_MAIN_BRANCH}'.")
    click.echo(f"Workload GitOps code creation completed in {time.time() - func_start_time:.2f} seconds.")


def add_workload_and_commit(
        gor: PlatformGitOpsRepo, wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str
) -> None:
    """
    Add the workload to the GitOps repository and commit changes.

    Parameters:
        gor: PlatformGitOpsRepo class instance.
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.
    """
    gor.add_workload(wl_name, wl_repo_name, wl_gitops_repo_name)
    gor.upload_changes()
    logger.info("Workload added and committed to the repository.")
