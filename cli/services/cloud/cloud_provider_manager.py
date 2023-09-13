class CloudProviderManager:
    """Cloud provider SDK wrapper to standardise cloud provider management."""

    def detect_cli_presence(self) -> bool:
        """
        Check if cloud provider CLI tools are installed
        :return: True or False
        """
        pass

    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        pass

    def create_iac_state_storage(self, bucket: str):
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        pass

    def create_iac_backend_snippet(self, location: str, region: str = None):
        """
        Creates terraform backend snippet
        :return: Code snippet
        """
        pass

    def create_hosting_provider_snippet(self, location: str, region: str = None):
        """
        Creates terraform hosting provider snippet
        :return: Code snippet
        """
        pass
