import time

import click

from common.const.const import WL_REPOSITORY_BRANCH, WL_PR_BRANCH_NAME_PREFIX
from common.custom_excpetions import GitBranchAlreadyExists, PullRequestCreationError
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import str_to_kebab, check_installation_presence, \
    initialize_gitops_repository, create_and_setup_branch, create_and_open_pull_request
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
    '--workload-gitops-main-branch-name',
    '-wlgmbn',
    'main_branch',
    default=WL_REPOSITORY_BRANCH,
    help='Workload GitOps repository main branch name', type=click.STRING
)
@click.option(
    '--verbosity',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
    default='CRITICAL',
    help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
)
def create(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, main_branch: str, verbosity: str) -> None:
    """
    Create workload boilerplate for GitOps.

    Parameters:
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.
        main_branch (str): Main branch name of the GitOps repository.
        verbosity (str): Logging level.
    """
    func_start_time = time.time()
    click.echo("Initializing workload GitOps code creation...")
    branch_name = f"{WL_PR_BRANCH_NAME_PREFIX}{wl_name}-init"

    configure_logging(verbosity)
    check_installation_presence()

    state_store = StateStore()
    click.echo("1/7: State store initialized.")

    wl_name, wl_repo_name, wl_gitops_repo_name = _process_workload_names(
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("2/7: Workload names processed.")

    git_man, gor = initialize_gitops_repository(state_store=state_store, logger=logger)
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
            wl_name=wl_name,
            branch_name=branch_name,
            main_branch=main_branch,
            logger=logger
        )
    except PullRequestCreationError as e:
        raise click.ClickException(str(e))

    click.echo(f"6/7: Pull request for branch '{branch_name}' created and opened in the web browser.")

    gor.switch_to_branch(branch_name=main_branch)
    click.echo(f"7/7: Switched to branch '{main_branch}'.")
    click.echo(f"Workload GitOps code creation completed in {time.time() - func_start_time:.2f} seconds.")


def _process_workload_names(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str) -> tuple[str, str, str]:
    """
    Process and normalize workload names to a standard format.

    Parameters:
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.

    Returns:
        tuple[str, str, str]: Tuple of processed workload name, workload repository name, and GitOps repository name.
    """
    logger.debug(f"Processing workload names: {wl_name}, {wl_repo_name}, {wl_gitops_repo_name}")
    processed_wl_name = str_to_kebab(wl_name)
    processed_wl_repo_name = str_to_kebab(wl_repo_name or wl_name)
    processed_wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name or f"{wl_repo_name}-gitops")
    logger.info(f"Processed names: {processed_wl_name}, {processed_wl_repo_name}, {processed_wl_gitops_repo_name}")
    return processed_wl_name, processed_wl_repo_name, processed_wl_gitops_repo_name


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
