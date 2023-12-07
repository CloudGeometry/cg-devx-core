import json
import os
import time
from re import sub

import requests
from git import Repo
from requests import HTTPError

from common.const.common_path import LOCAL_GITOPS_FOLDER
from common.const.parameter_names import CLOUD_REGION, CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET, GIT_ACCESS_TOKEN, \
    GIT_ORGANIZATION_NAME
from common.enums.cloud_providers import CloudProviders
from common.enums.dns_registrars import DnsRegistrars
from common.enums.git_providers import GitProviders
from common.logging_config import logger
from common.retry_decorator import exponential_backoff
from common.state_store import StateStore
from services.cloud.aws.aws_manager import AWSManager
from services.cloud.azure.azure_manager import AzureManager
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.dns.azure_dns.azure_dns import AzureDNSManager
from services.dns.dns_provider_manager import DNSManager
from services.dns.route53.route53 import Route53Manager
from services.vcs.git_provider_manager import GitProviderManager
from services.vcs.github.github_manager import GitHubProviderManager
from services.vcs.gitlab.gitlab_manager import GitLabProviderManager


def init_cloud_provider(state: StateStore) -> tuple[CloudProviderManager, DNSManager]:
    cloud_manager: CloudProviderManager = None
    domain_manager: DNSManager = None
    # init proper cloud provider

    if state.cloud_provider == CloudProviders.AWS:
        cloud_manager: AWSManager = AWSManager(state.get_input_param(CLOUD_REGION),
                                               state.get_input_param(CLOUD_PROFILE),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))

        # check if cloud native DNS registrar is selected
        if state.dns_registrar == DnsRegistrars.Route53:
            # Note!: Route53 is initialised with AWS Cloud Provider
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
        cloud_manager: AzureManager = AzureManager(
            state.get_input_param(CLOUD_PROFILE), state.get_input_param(CLOUD_REGION)
        )
        domain_manager: DNSManager = AzureDNSManager(state.get_input_param(CLOUD_PROFILE))

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


def prepare_cloud_provider_auth_env_vars(state: StateStore):
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


def update_gitops_repo():
    repo = Repo(LOCAL_GITOPS_FOLDER)
    # clean stale branches
    repo.remotes.origin.fetch(prune=True)
    # update repo just in case
    repo.heads.main.checkout()
    repo.remotes.origin.pull(repo.active_branch)
    return repo


def create_pr(org_name: str, repo_name: str, token: str, head_branch: str, base_branch: str, title: str,
              body: str) -> bool:
    git_pulls_api = f"https://api.github.com/repos/{org_name}/{repo_name}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }
    res = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload))

    if not res.ok:
        logger.error("GitHub API Request Failed: {0}".format(res.text))
        return False

    return True
