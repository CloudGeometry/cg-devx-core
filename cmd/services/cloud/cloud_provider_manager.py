class CloudProviderManager:
    """Cloud provider SDK wrapper to standardise cloud provider management."""

    def detect_cli_presence(self):
        """
        Check if cloud provider CLI tools are installed
        :return: True or False
        """
        pass

    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
            """
        pass

    def create__iac_state_storage(self):
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        pass
