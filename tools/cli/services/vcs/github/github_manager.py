import json
from urllib.error import HTTPError

import requests

from common.const.const import FALLBACK_AUTHOR_NAME, FALLBACK_AUTHOR_EMAIL
from common.tracing_decorator import trace
from services.vcs.git_provider_manager import GitProviderManager


class GitHubProviderManager(GitProviderManager):
    """GitHub provider wrapper."""

    def __init__(self, token: str = None, org_name: str = None):
        self.__token: str = token
        self.__org_name: str = org_name
        self.__required_scopes = {
            "admin:org", "admin:org_hook", "admin:public_key", "admin:repo_hook", "admin:ssh_signing_key",
            "delete_repo", "repo"
        }

    @trace()
    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if repository exists
        :return: True or False
        """
        headers = {
            'Authorization': f'token {self.__token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        try:
            response = requests.get(f'https://api.github.com/repos/{self.__org_name}/{name}', headers=headers)
            if response.status_code == requests.codes["not_found"]:
                return False
            elif response.ok:
                return True
        except HTTPError as e:
            raise e

    @trace()
    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        headers = {
            'Authorization': f'token {self.__token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        try:
            response = requests.head('https://api.github.com', headers=headers)
            if "x-oauth-scopes" not in response.headers:
                return False
            allowed_scopes = response.headers["x-oauth-scopes"].split(", ")
            # check if we need those permissions "workflow", "write:packages", "user"
            return self.__required_scopes.issubset(allowed_scopes)
        except HTTPError as e:
            return False

    @trace()
    def get_current_user_info(self):
        """
        Get authenticated user info
        :return: Login, Name, Email
        """
        headers = {
            'Authorization': f'token {self.__token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        try:
            response = requests.get('https://api.github.com/user', headers=headers)
            res = json.loads(response.text)

            if res["name"] is None:
                name = FALLBACK_AUTHOR_NAME
            else:
                name = res["name"]

            if res["email"] is None:
                email = FALLBACK_AUTHOR_EMAIL
            else:
                email = res["email"]
            return res["login"], name, email
        except HTTPError as e:
            raise e

    @trace()
    def create_tf_module_snippet(self):
        return 'provider "github" {}'
