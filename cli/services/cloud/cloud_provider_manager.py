class CloudProviderManager:
    """Cloud provider SDK wrapper to standardise cloud provider management."""

    @property
    def region(self) -> str:
        pass

    @property
    def account_id(self) -> str:
        pass

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

    def destroy_iac_state_storage(self, bucket: str):
        """
        Destroy cloud native terraform remote state storage
        """
        pass

    def create_iac_backend_snippet(self, location: str, region: str = None, service="default"):
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

    def create_k8s_role_binding_snippet(self):
        """
        Creates service account - IAM role binding snippet
        :return: Code snippet
        """
        pass

    def get_k8s_auth_command(self) -> str:
        """
        Returns kubeconfig cluster aut command
        :return: command
        """
        pass

    def get_k8s_token(self, cluster_name: str) -> str:
        """
        Creates K8s cluster API key
        :return: API key
        """
        pass
