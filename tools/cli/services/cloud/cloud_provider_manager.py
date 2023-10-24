from abc import ABC, abstractmethod


class CloudProviderManager(ABC):
    """Cloud provider SDK wrapper to standardise cloud provider management."""

    @property
    def region(self) -> str:
        pass

    @abstractmethod
    def detect_cli_presence(self) -> bool:
        """
        Check if cloud provider CLI tools are installed
        :return: True or False
        """
        pass

    @abstractmethod
    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        pass

    @abstractmethod
    def create_iac_state_storage(self, name: str, **kwargs: dict) -> str:
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        pass

    @abstractmethod
    def destroy_iac_state_storage(self, bucket: str):
        """
        Destroy cloud native terraform remote state storage
        """
        pass

    @abstractmethod
    def create_iac_backend_snippet(self, location: str, service: str = "default", **kwargs: dict):
        """
        Creates terraform backend snippet
        :return: Code snippet
        """
        pass

    @abstractmethod
    def create_hosting_provider_snippet(self):
        """
        Creates terraform hosting provider snippet
        :return: Code snippet
        """
        pass

    @abstractmethod
    def create_secret_manager_seal_snippet(self, key_id: str):
        """
        Creates helm vault seal snippet
        :return: Helm snippet
        """
        pass

    @abstractmethod
    def create_k8s_cluster_role_mapping_snippet(self):
        """
        Creates K8s cluster role binding snippet
        :return: Code snippet
        """
        pass

    @abstractmethod
    def get_k8s_auth_command(self):
        """
        Returns kubeconfig cluster aut command
        :return: command
        """
        pass

    @abstractmethod
    def get_k8s_token(self, cluster_name: str) -> str:
        """
        Creates K8s cluster API key
        :return: API key
        """
        pass
