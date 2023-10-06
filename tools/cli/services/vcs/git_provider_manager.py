from abc import ABC, abstractmethod


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
