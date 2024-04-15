import os
import os
import time
import webbrowser
from logging import Logger
from re import sub
from typing import Optional

import click
import requests
from requests import HTTPError

from common.const.common_path import LOCAL_GITOPS_FOLDER, LOCAL_FOLDER
from common.const.parameter_names import CLOUD_REGION, CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET, GIT_ACCESS_TOKEN, \
    GIT_ORGANIZATION_NAME
from common.custom_excpetions import GitBranchAlreadyExists, PullRequestCreationError
from common.enums.cloud_providers import CloudProviders
from common.enums.dns_registrars import DnsRegistrars
from common.enums.git_providers import GitProviders
from common.retry_decorator import exponential_backoff
from common.state_store import StateStore
from services.cloud.aws.aws_manager import AWSManager
from services.cloud.azure.azure_manager import AzureManager
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.dns.azure_dns.azure_dns import AzureDNSManager
from services.dns.dns_provider_manager import DNSManager
from services.dns.route53.route53 import Route53Manager
from services.platform_gitops import PlatformGitOpsRepo
from services.vcs.git_provider_manager import GitProviderManager
from services.vcs.github.github_manager import GitHubProviderManager
from services.vcs.gitlab.gitlab_manager import GitLabProviderManager


def init_cloud_provider(state: StateStore) -> tuple[CloudProviderManager, DNSManager]:
    cloud_manager: CloudProviderManager = None
    domain_manager: DNSManager = None

    # init proper cloud provider
    if state.cloud_provider == CloudProviders.AWS:
        # need to check CLI dependencies before initializing cloud providers as they depend on cli tools
        if not AWSManager.detect_cli_presence():
            raise click.ClickException("Cloud CLI is missing")

        cloud_manager: AWSManager = AWSManager(state.get_input_param(CLOUD_REGION),
                                               state.get_input_param(CLOUD_PROFILE),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))

        # check if cloud native DNS registrar is selected
        if state.dns_registrar == DnsRegistrars.Route53:
            # Note!: Route53 is initialized with AWS Cloud Provider
            if state.get_input_param(DNS_REGISTRAR_ACCESS_KEY) is None and state.get_input_param(
                    DNS_REGISTRAR_ACCESS_SECRET) is None:
                # initialize with cloud account permissions
                domain_manager: DNSManager = Route53Manager(profile=state.get_input_param(CLOUD_PROFILE),
                                                            key=state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                                            secret=state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))
            else:
                # initialize with a provided key and secret
                domain_manager: DNSManager = Route53Manager(
                    key=state.get_input_param(DNS_REGISTRAR_ACCESS_KEY),
                    secret=state.get_input_param(DNS_REGISTRAR_ACCESS_SECRET))

    elif state.cloud_provider == CloudProviders.Azure:
        # need to check CLI dependencies before initializing cloud providers as they depend on cli tools
        if not AzureManager.detect_cli_presence():
            raise click.ClickException("Cloud CLI is missing")

        subscription_id = state.get_input_param(CLOUD_PROFILE)
        cloud_manager: AzureManager = AzureManager(
            subscription_id, state.get_input_param(CLOUD_REGION)
        )
        domain_manager: DNSManager = AzureDNSManager(state.get_input_param(CLOUD_PROFILE))
        state.parameters["<AZ_SUBSCRIPTION_ID>"] = subscription_id

    return cloud_manager, domain_manager


def init_git_provider(state: StateStore) -> GitProviderManager:
    # init proper git provider
    if state.git_provider == GitProviders.GitHub:
        git_man: GitProviderManager = GitHubProviderManager(state.get_input_param(GIT_ACCESS_TOKEN),
                                                            state.get_input_param(GIT_ORGANIZATION_NAME))
    elif state.git_provider == GitProviders.GitLab:
        git_man: GitProviderManager = GitLabProviderManager(
            state.get_input_param(GIT_ACCESS_TOKEN),
            state.get_input_param(GIT_ORGANIZATION_NAME)
        )
    else:
        raise Exception('Error: None of the available Git providers were specified')

    return git_man


def prepare_cloud_provider_auth_env_vars(state: StateStore) -> dict:
    if state.cloud_provider == CloudProviders.AWS:
        # drop empty values
        cloud_provider_auth_env_vars = {
            "AWS_PROFILE": state.get_input_param(CLOUD_PROFILE),
            "AWS_ACCESS_KEY_ID": state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
            "AWS_SECRET_ACCESS_KEY": state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET),
            "AWS_REGION": state.parameters["<CLOUD_REGION>"],
            "AWS_DEFAULT_REGION": state.parameters["<CLOUD_REGION>"],
        }
    elif state.cloud_provider == CloudProviders.Azure:
        cloud_provider_auth_env_vars = {}
    else:
        cloud_provider_auth_env_vars = {}
    return cloud_provider_auth_env_vars


def prepare_git_provider_env_vars(state: StateStore) -> dict:
    if state.git_provider == GitProviders.GitHub:
        return {
            "GITHUB_TOKEN": state.get_input_param(GIT_ACCESS_TOKEN),
            "GITHUB_OWNER": state.get_input_param(GIT_ORGANIZATION_NAME)
        }
    elif state.git_provider == GitProviders.GitLab:
        return {"GITLAB_TOKEN": state.get_input_param(GIT_ACCESS_TOKEN)}


def set_envs(env_vars):
    for k, vault_i in env_vars.items():
        if vault_i:
            os.environ[k] = vault_i


def unset_envs(env_vars):
    for k, vault_i in env_vars.items():
        if vault_i:
            os.environ.pop(k)


def wait(seconds: float = 15):
    time.sleep(seconds)


@exponential_backoff()
def wait_http_endpoint_readiness(endpoint: str):
    try:
        response = requests.get(endpoint,
                                verify=False,
                                headers={"Content-Type": "application/json"},
                                )
        if response.ok:
            return
        else:
            raise Exception(f"Endpoint {endpoint} not ready.")
    except HTTPError as e:
        return


def str_to_kebab(string: str):
    """
    Convert string to kebab case
    :param string: input string
    :return: kebab string
    """
    return '-'.join(
        sub(r"(\s|_|-)+", " ",
            sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda match: ' ' + match.group(0).lower(), string)).split())


def check_installation_presence():
    if not os.path.exists(LOCAL_FOLDER):
        raise click.ClickException("CG DevX metadata does not exist on this machine")


def initialize_gitops_repository(
        state_store: StateStore, logger: Logger
) -> tuple[GitProviderManager, PlatformGitOpsRepo]:
    """
    Initialize and return the GitOps repository manager.

    This function sets up the GitOps repository manager using the provided state store configuration.
    It initializes a GitOps repository object with necessary authentication and configuration details.

    Parameters:
        state_store (StateStore): An instance of StateStore containing configuration and state information.
        logger (Logger): A logger instance for logging the process.

    Returns:
        tuple: A tuple containing the Git manager and GitOps repository instance.
               The Git manager is used for Git operations, while the GitOps repository instance
               is a specific repository related to GitOps operations.

    The function updates the GitOps repository to ensure it is synchronized with its remote version and logs
     the initialization process.
    """
    git_man = init_git_provider(state_store)
    gor = PlatformGitOpsRepo(
        git_man=git_man,
        author_name=state_store.internals["GIT_USER_NAME"],
        author_email=state_store.internals["GIT_USER_EMAIL"],
        key_path=state_store.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"],
        repo_remote_url=state_store.parameters.get("<GIT_REPOSITORY_GIT_URL>")
    )
    gor.update()
    logger.info("GitOps repository initialized.")
    return git_man, gor


def create_and_setup_branch(gor: PlatformGitOpsRepo, branch_name: str, logger: Logger) -> None:
    """
    Create and set up a new branch for the workload in the GitOps repository.

    This function tries to create a new branch with the given name in the GitOps repository.
    If the branch creation fails due to the branch already existing, it raises a
    BranchAlreadyExistsException.

    Parameters:
        gor (PlatformGitOpsRepo): Instance of the GitOps repository.
        branch_name (str): Name of the branch to be created.
        logger (Logger): A logger instance for logging the process.

    Raises:
        BranchAlreadyExistsException: If the branch already exists in the repository.
    """
    try:
        logger.debug(f"Attempting to create branch '{branch_name}' in the GitOps repository.")
        gor.create_branch(branch_name)
        logger.info(f"Branch '{branch_name}' created successfully.")
    except OSError as e:
        logger.error(f"Error occurred while creating branch '{branch_name}': {e}")
        raise GitBranchAlreadyExists(branch_name)


def create_and_open_pull_request(
        gor: PlatformGitOpsRepo,
        state_store: StateStore,
        title: str,
        body: str,
        branch_name: str,
        main_branch: str,
        logger: Logger
) -> None:
    """
    Create a pull request for the workload and open it in a web browser.

    Parameters:
        gor: PlatformGitOpsRepo class instance.
        state_store (StateStore): State store instance for accessing configuration.
        title (str): PR title.
        body (str): PR body.
        branch_name (str): The branch for which the pull request is created.
        main_branch (str): Main branch of the repository.
        logger (Logger): A logger instance for logging the process.
    """
    try:
        pr_url = gor.create_pr(
            state_store.parameters["<GITOPS_REPOSITORY_NAME>"], branch_name, main_branch,
            title, body
        )
        webbrowser.open(pr_url, autoraise=False)
        logger.info(f"Pull request created: {pr_url}")
    except Exception as e:
        logger.error(f"Error in creating pull request: {e}")
        raise PullRequestCreationError(f"Could not create PR due to: {e}")


def preprocess_workload_names(
        logger: Logger,
        wl_name: str, wl_repo_name: Optional[str] = None, wl_gitops_repo_name: Optional[str] = None
) -> tuple[str, str, str]:
    """
    Process and normalize workload names to a standard format.

    Parameters:
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.
        logger (Logger): A logger instance for logging the process.

    Returns:
        tuple[str, str, str]: Tuple of processed workload name, workload repository name, and GitOps repository name.
    """
    logger.debug(f"Processing workload names: {wl_name}, {wl_repo_name}, {wl_gitops_repo_name}")
    wl_name = str_to_kebab(wl_name)
    wl_repo_name = str_to_kebab(wl_repo_name or wl_name)
    wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name or f"{wl_repo_name}-gitops")
    logger.info(f"Processed names: {wl_name}, {wl_repo_name}, {wl_gitops_repo_name}")
    return wl_name, wl_repo_name, wl_gitops_repo_name


def construct_wl_iam_role(
        cloud_provider: CloudProviders,
        cloud_account: str,
        cluster_name: str,
        wl_name: str,
        wl_svc_name: str):
    """
    Creates cloud-provider-specific workload IAM role name used for K8s role mapping annotations.

    Parameters:
        cloud_provider (CloudProviders): Cloud provider
        cloud_account (str): Cloud account
        cluster_name (str): K8s cluster name
        wl_name (str): Workload name
        wl_svc_name (str): Workload service name

    Returns:
        str: Role name
    """
    if cloud_provider == CloudProviders.AWS:
        return f"arn:aws:iam::{cloud_account}:role/{cluster_name}-{wl_name}-{wl_svc_name}-role"
    else:
        return "<set workload role mapping here>"
