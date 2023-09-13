class GitProviderManager:
    """Git provider wrapper to standardise Git management."""

    def check_repository_existence(self, name: str = "GitOps"):
        """
        Check if repository exists
        :return: True or False
        """
        pass

    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
            """
        pass

    def create_tf_module_snippet(self):
        """
        Create tf git provider snippet
        :return: Snippet
            """
        pass