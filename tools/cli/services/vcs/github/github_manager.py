import json
import textwrap
from urllib.error import HTTPError

import requests
from ghrepo import GHRepo

from common.const.const import FALLBACK_AUTHOR_NAME, FALLBACK_AUTHOR_EMAIL
from common.enums.git_plans import GitSubscriptionPlans
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

    @property
    def organization(self) -> str:
        return self.__org_name

    @trace()
    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if the repository exists
        :return: True or False
        """
        headers = self._generate_headers()
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
        headers = self._generate_headers()
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
        headers = self._generate_headers()
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

    @trace()
    def create_tf_required_provider_snippet(self) -> str:
        """
        Generates a multiline string containing a Terraform configuration snippet

        This function creates a configuration snippet for the GitHub provider, which includes
        details such as the source and version of the provider.

        :return: A multiline string containing the GitHub provider configuration snippet.
        :rtype: str
        """
        return textwrap.dedent("""\
        github = {
              # https://registry.terraform.io/providers/integrations/github/latest/docs
              source  = "integrations/github"
              version = "~> <GITHUB_PROVIDER_VERSION>"
            }""")

    @trace()
    def create_runner_group_snippet(self) -> str:
        return 'group: <GIT_RUNNER_GROUP_NAME>'

    @trace()
    def get_organization_plan(self) -> GitSubscriptionPlans:
        """
        Get active plan, if present
        :return: Plan name
        """
        headers = self._generate_headers()
        try:
            response = requests.get(f'https://api.github.com/orgs/{self.__org_name}', headers=headers)
            if response.ok:
                res = json.loads(response.text)

                plan_name = res["plan"]["name"]
                if plan_name == "pro":
                    return GitSubscriptionPlans.Enterprise
                elif plan_name == "team":
                    return GitSubscriptionPlans.Pro
                elif plan_name == "free":
                    return GitSubscriptionPlans.Free
                else:
                    return GitSubscriptionPlans.Free
            else:
                raise Exception("Org not found")
        except HTTPError as e:
            raise e

    @trace()
    def create_pr(self, repo_name: str, head_branch: str, base_branch: str, title: str, body: str) -> str:
        git_pulls_api = f"https://api.github.com/repos/{self.__org_name}/{repo_name}/pulls"
        headers = self._generate_headers()
        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch
        }
        try:
            res = requests.post(
                git_pulls_api,
                headers=headers,
                data=json.dumps(payload))

            if not res.ok:
                raise Exception("GitHub API Request Failed: {0}".format(res.text))

            data = json.loads(res.text)

            return data["html_url"]
        except HTTPError as e:
            raise e

    def _generate_headers(self):
        headers = {
            "Authorization": f"token {self.__token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        return headers

    def create_iac_pr_automation_config_snippet(self):
        """
        Creates GitHub specific configuration section for Atlantis
        :return: Atlantis configuration section
        """
        return textwrap.dedent("""# github specific section
      ATLANTIS_GH_HOSTNAME                 = "github.com",
      ATLANTIS_GH_TOKEN                    = var.vcs_token,
      ATLANTIS_GH_USER                     = "<GIT_USER_LOGIN>",
      ATLANTIS_GH_WEBHOOK_SECRET           = var.atlantis_repo_webhook_secret,
      GITHUB_OWNER                         = "<GIT_ORGANIZATION_NAME>",
      GITHUB_TOKEN                         = var.vcs_token,
      # ----""")

    def get_repository_root(self) -> str:
        """
        Retrieves the base URL segment for GitHub repositories under the specified organization.

        This method returns the starting segment of the URL used to access repositories within a specific GitHub
        organization via its web interface.
        It provides a foundational URL segment, which can be used as the base in constructing URLs for specific
        repositories or further navigation within the GitHub organization.

        :return: The base segment of the GitHub URL for the specified organization, suitable for constructing more
        specific repository URLs.
        :rtype: str
        """
        return f"github.com/{self.__org_name}"

    def get_repository_url(self, org_name: str, repo_name: str) -> str:
        """
        Retrieve the SSH URL of a GitHub repository.

        :param org_name: The name of the GitHub organization or group.
        :param repo_name: The name of the repository.
        :return: The SSH URL of the repository.
        :raises HTTPError: If there is an issue with the API request.
        """
        return GHRepo(owner=org_name, name=repo_name).ssh_url

    def get_repository_hostname(self) -> str:
        """
        Retrieves the hostname for GitHub repository.

        This method returns the GitHub repo hostname.

        :return: The GitHub repo hostname.
        :rtype: str
        """
        return "github.com"
