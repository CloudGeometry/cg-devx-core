import webbrowser

import click

from common.utils.command_utils import str_to_kebab, init_git_provider, check_installation_presence
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from services.platform_gitops import PlatformGitOpsRepo

DEFAULT_MAIN_BRANCH = "main"
BRANCH_NAME_PREFIX = "feature/"


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option(
    '--workload-repository-name',
    '-wlrn', 'wl_repo_name',
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
    '-wlgmbn', 'main_branch',
    default=DEFAULT_MAIN_BRANCH,
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
    click.echo("Initializing workload GitOps code creation...")
    branch_name = f"{BRANCH_NAME_PREFIX}{wl_name}-init"

    configure_logging(verbosity)
    check_installation_presence()

    state_store = StateStore()
    click.echo("[1/7] State store initialized.")

    wl_name, wl_repo_name, wl_gitops_repo_name = process_workload_names(
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("[2/7] Workload names processed.")

    git_man, gor = initialize_gitops_repository(state_store=state_store)
    click.echo("[3/7] GitOps repository initialized.")

    create_and_setup_branch(gor=gor, branch_name=branch_name)
    click.echo(f"[4/7] Branch '{branch_name}' created and set up.")

    add_workload_and_commit(
        gor=gor,
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("[5/7] Workload added and changes committed.")

    create_and_open_pull_request(
        gor=gor,
        state_store=state_store,
        wl_name=wl_name,
        branch_name=branch_name,
        main_branch=main_branch
    )
    click.echo(f"[6/7] Pull request for branch '{branch_name}' created and opened in the web browser.")

    gor.switch_to_branch(branch_name=main_branch)
    click.echo(f"[7/7] Switched to branch '{main_branch}'.")
    click.echo("Workload GitOps code creation complete.")


def process_workload_names(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str) -> tuple[str, str, str]:
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


def initialize_gitops_repository(state_store: StateStore) -> tuple:
    """
    Initialize and return the GitOps repository manager.

    Parameters:
        state_store (StateStore): State store instance for accessing configuration.

    Returns:
        tuple: Tuple containing git manager and GitOps repository instance.
    """
    git_man = init_git_provider(state_store)
    gor = PlatformGitOpsRepo(
        git_man=git_man,
        author_name=state_store.internals["GIT_USER_NAME"],
        author_email=state_store.internals["GIT_USER_EMAIL"],
        key_path=state_store.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]
    )
    gor.update()
    logger.info("GitOps repository initialized.")
    return git_man, gor


def create_and_setup_branch(gor: PlatformGitOpsRepo, branch_name: str) -> None:
    """
    Create and set up a new branch for the workload.

    Parameters:
        gor: PlatformGitOpsRepo class instance.
        branch_name (str): The name of the branch to create.
    """
    if gor.branch_exist(branch_name):
        logger.error(f"Branch {branch_name} already exists.")
        raise click.ClickException("Branch already exists, please use a different workload name.")
    gor.create_branch(branch_name)
    logger.info(f"Branch {branch_name} created.")


def create_and_open_pull_request(
        gor: PlatformGitOpsRepo,
        state_store: StateStore,
        wl_name: str,
        branch_name: str,
        main_branch: str
) -> None:
    """
    Create a pull request for the workload and open it in a web browser.

    Parameters:
        gor: PlatformGitOpsRepo class instance.
        state_store (StateStore): State store instance for accessing configuration.
        wl_name (str): Name of the workload.
        branch_name (str): The branch for which the pull request is created.
        main_branch (str): Main branch of the repository.
    """
    try:
        pr_url = gor.create_pr(
            state_store.parameters["<GITOPS_REPOSITORY_NAME>"], branch_name, main_branch,
            f"Introduce {wl_name}", "Add default secrets, groups and default repository structure."
        )
        webbrowser.open(pr_url, autoraise=False)
        logger.info(f"Pull request created: {pr_url}")
    except Exception as e:
        logger.error(f"Error in creating pull request: {e}")
        raise click.ClickException("Could not create PR")


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
