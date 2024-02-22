import json
import textwrap
from typing import Dict, Optional, Union, Tuple

import requests
from requests.exceptions import HTTPError

from common.const.const import FALLBACK_AUTHOR_NAME, FALLBACK_AUTHOR_EMAIL
from common.enums.git_plans import GitSubscriptionPlans
from common.tracing_decorator import trace
from services.vcs.git_provider_manager import GitProviderManager


class GitLabProviderManager(GitProviderManager):
    """GitLab provider wrapper."""
    __BASE_API_URI = "https://gitlab.com/api/v4"

    def __init__(self, token: str, group_name: str):
        """
        Initialize a new instance of the GitLabProviderManager.

        :param token: GitLab API token for authentication.
        :param group_name: GitLab group name for which the permissions are evaluated.
        """
        self.__token = token
        self.__group_name = group_name
        self.__required_role = 40  # Maintainer
        self.__required_token_scope = {"api"}

    def _get_headers(self) -> Dict[str, str]:
        """
        Construct and return headers for GitLab API requests.

        :return: Dictionary containing the necessary headers for the API call.
        """
        return {
            "Authorization": f"Bearer {self.__token}",
            "Accept": "application/json"
        }

    @property
    def organization(self) -> str:
        return self.__group_name

    @trace()
    def check_repository_existence(self, name: str = "GitOps") -> bool:
        """
        Check if a given repository exists within the specified GitLab group.

        :param name: Name of the repository to check. Default is "GitOps".
        :return: True if repository exists, False otherwise.
        :raises HTTPError: If there's an issue with the API request.
        """
        headers = {
            "Private-Token": f"{self.__token}",
        }
        try:
            response = requests.get(url=f"{self.__BASE_API_URI}/projects/{self.__group_name}%2F{name}", headers=headers)
            if response.status_code == 404:
                return False
            elif response.status_code == 200:
                return True
        except HTTPError as e:
            raise e

    def _get_group_id_by_group_name(self) -> Optional[int]:
        """
        Retrieve the GitLab group ID based on the group name.

        :return: ID of the GitLab group or None if the group is not found or an error occurs.
        """
        headers = self._get_headers()
        try:
            response = requests.get(url=f"{self.__BASE_API_URI}/groups?search={self.__group_name}", headers=headers)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            # Attempt to get the ID of the first group. If groups are empty, this will raise an IndexError
            first_group = response.json()[0]
            return first_group.get("id")

        except (IndexError, KeyError, requests.RequestException):
            return None

    def _retrieve_token_data(self) -> Dict[str, Union[str, int, list]]:
        """
        Fetch the token's details, including active scopes, from the GitLab API.

        :return: Dictionary containing token details or an empty dictionary if an error occurs.
        """
        try:
            response = requests.get(
                url=f"{self.__BASE_API_URI}/personal_access_tokens/self",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}

    def _get_user_role(self, group_id: int, user_id: int) -> Optional[int]:
        """
        Retrieve the user's role in the specified GitLab group.

        :param group_id: ID of the GitLab group.
        :param user_id: ID of the user.
        :return: User's role (as an integer) in the group or None if an error occurs.
        """
        try:
            response = requests.get(
                url=f"{self.__BASE_API_URI}/groups/{group_id}/members/{user_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json().get("access_level")
        except requests.RequestException:
            return None

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have the required permissions on GitLab for the specified group.

        :return: True if permissions are satisfied, otherwise False.
        """
        try:
            # Retrieve the GitLab group ID based on its name
            group_id = self._get_group_id_by_group_name()

            # Fetch token-related data (like scopes and user ID) from GitLab API
            token_data = self._retrieve_token_data()

            # Extract the list of scopes associated with the token
            token_scopes = token_data["scopes"]

            # Extract the user ID associated with the token
            user_id = token_data["user_id"]

            # Fetch the user's role within the specified group
            user_role = self._get_user_role(group_id, user_id)
            # Evaluate and return True if the user's role meets or exceeds the required role
            # and the token's scopes include all required scopes; otherwise, return False
            return user_role >= self.__required_role and self.__required_token_scope.issubset(token_scopes)

        except (KeyError, TypeError):
            # This will handle cases where keys are missing from dicts, or None values are used inappropriately
            return False

    @trace()
    def get_current_user_info(self) -> Tuple[str, str, str]:
        """
        Retrieve authenticated user's information from GitLab.

        :return: Tuple containing the username, name, and email of the authenticated user.
        :raises HTTPError: If there's an issue with the API request.
        """
        headers = {
            "Private-Token": f"{self.__token}",
        }
        try:
            response = requests.get(url=f"{self.__BASE_API_URI}/user", headers=headers)
            res = json.loads(response.text)

            name = res.get("name", FALLBACK_AUTHOR_NAME)
            email = res.get("email", FALLBACK_AUTHOR_EMAIL)

            return res["username"], name, email
        except HTTPError as e:
            raise e

    @trace()
    def create_tf_module_snippet(self) -> str:
        """
        Generate a Terraform module snippet for the GitLab provider.

        :return: A string containing the Terraform module snippet.
        """
        return "provider \"gitlab\" {}"

    @trace()
    def create_tf_required_provider_snippet(self) -> str:
        """
        Generates a multiline string containing a Terraform configuration snippet

        This function creates a configuration snippet for the GitLab provider, which includes
        details such as the source and version of the provider.

        :return: A multiline string containing the GitLab provider configuration snippet.
        :rtype: str
        """
        return textwrap.dedent("""\
        gitlab = {
              # https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs
              source  = "gitlabhq/gitlab"
              version = "<GITLAB_PROVIDER_VERSION>"
            }""")

    @trace()
    def create_runner_group_snippet(self) -> str:
        return ''

    @trace()
    def get_organization_plan(self) -> GitSubscriptionPlans:
        """
        Get active plan, if present
        :return: Plan name
        """
        return GitSubscriptionPlans.Free

    @trace()
    def create_pr(self, repo_name: str, head_branch: str, base_branch: str, title: str, body: str) -> str:
        pass
