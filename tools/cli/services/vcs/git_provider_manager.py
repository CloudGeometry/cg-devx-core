from abc import ABC, abstractmethod

from common.enums.git_plans import GitSubscriptionPlans


class GitProviderManager(ABC):
    """Git provider wrapper to standardise Git management."""

    @abstractmethod
    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if repository exists
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
    def get_organization_plan(self, organization_name: str) -> [str, GitSubscriptionPlans]:
        """
        Get active plan, if present
        :return: Subscription plan
        """
        pass
