from abc import ABC, abstractmethod

from common.enums.git_plans import GitSubscriptionPlans


class GitProviderManager(ABC):
    """Git provider wrapper to standardise Git management."""
    @property
    def organization(self) -> str:
        pass

    @abstractmethod
    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if the repository exists
        :return: True or False
        """
        pass

    @abstractmethod
    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        pass

    @abstractmethod
    def create_tf_module_snippet(self):
        """
        Create tf git provider snippet
        :return: Snippet
        """
        pass

    @abstractmethod
    def create_tf_required_provider_snippet(self) -> str:
        """
        Generates a multiline string containing a Terraform configuration snippet

        This function creates a configuration snippet for the Git provider, which includes
        details such as the source and version of the provider.

        :return: A multiline string containing the Git provider configuration snippet.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_current_user_info(self):
        """
        Get authenticated user info
        :return: Login, Name, Email
        """
        pass

    @abstractmethod
    def create_runner_group_snippet(self) -> str:
        """
        Create external CI/CD runner group snippet
        :return: Snippet
        """
        pass

    @abstractmethod
    def get_organization_plan(self) -> GitSubscriptionPlans:
        """
        Get active plan, if present
        :return: Subscription plan
        """
        pass

    @abstractmethod
    def create_pr(self, repo_name: str, head_branch: str, base_branch: str, title: str, body: str) -> str:
        """
        Create a pull request
        :return: Pull request URL
        """
        pass
