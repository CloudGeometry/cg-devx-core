from urllib.error import HTTPError

import requests

from cli.services.vcs.git_provider_manager import GitProviderManager


class GitHubProviderManager(GitProviderManager):
    """GitHub provider wrapper."""

    def __init__(self, token: str = None, org_name: str = None):
        self.__token: str = token
        self.__org_name: str = org_name

    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if repository exists
        :return: True or False
        """
        headers = {
            'Authorization': f'token {self.__token}',
        }
        try:
            response = requests.get(f'https://api.github.com/repos/{self.__org_name}/{name}', headers=headers)
            if response.status_code == requests.codes["not_found"]:
                return False
            elif response.ok:
                return True
        except HTTPError as e:
            raise e

    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        headers = {
            'Authorization': f'token {self.__token}',
        }
        try:
            response = requests.head('https://api.github.com', headers=headers)
            if "x-oauth-scopes" not in response.headers:
                return False
            allowed_scopes = response.headers["x-oauth-scopes"].split(", ")
            # check if we need those permissions "workflow", "write:packages", "user"
            required_scopes = set(
                ["admin:org", "admin:org_hook", "admin:public_key", "admin:repo_hook", "admin:ssh_signing_key",
                 "delete_repo", "repo"])
            if required_scopes.issubset(allowed_scopes):
                return True
            else:
                return False
        except HTTPError as e:
            return False

    def _clone(self):
        pass
        # https://gitpython.readthedocs.io/en/stable/tutorial.html#tutorial-label
        # try:
        #     git.Repo.clone_from(f'https://null:null@github.com/{user.git_user}/{user.git_repos}.git',
        #                         f'temp/{user.name}/')
        # except git.exc.GitError:
        #     print(f'ERROR! {user.name}: {user.git_user}/{user.git_repos} does not exist')
        # repo = git.Repo.clone_from(self._small_repo_url(), os.path.join(rw_dir, "repo"), branch="master")
