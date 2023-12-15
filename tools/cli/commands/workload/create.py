import webbrowser

import click

from common.command_utils import str_to_kebab, init_git_provider, check_installation_presence
from common.logging_config import configure_logging
from common.state_store import StateStore
from services.platform_gitops import PlatformGitOpsRepo


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

    check_installation_presence()

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

    p: StateStore = StateStore()

    main_branch = "main"
    git_man = init_git_provider(p)
    gor = PlatformGitOpsRepo(git_man,
                             author_name=p.internals["GIT_USER_NAME"],
                             author_email=p.internals["GIT_USER_EMAIL"],
                             key_path=p.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"])
    # update repo just in case
    gor.update()

    # create new branch
    branch_name = f"feature/{wl_name}-init"
    gor.create_branch(branch_name)

    gor.add_workload(wl_name, wl_repo_name, wl_gitops_repo_name)

    # commit and prepare a PR
    gor.upload_changes()

    try:
        pr_url = gor.create_pr(p.parameters["<GITOPS_REPOSITORY_NAME>"],
                               branch_name,
                               main_branch,
                               f"introduce {wl_name}",
                               f"Add default secrets, user and default repository structure.")
        webbrowser.open(pr_url, autoraise=False)
    except Exception as e:
        raise click.ClickException("Could not create PR")

    gor.switch_to_branch()

    click.echo("Creating workload GitOps code. Done!")
    return True
