from abc import ABC, abstractmethod
from typing import Tuple


class CloudProviderManager(ABC):
    """Cloud provider SDK wrapper to standardise cloud provider management."""

    @property
    def region(self) -> str:
        """Cloud provider geographic area"""
        pass

    @property
    def account(self) -> str:
        """Cloud provider tenant"""
        pass

    @classmethod
    @abstractmethod
    def detect_cli_presence(cls) -> bool:
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
    def create_iac_state_storage(self, name: str, **kwargs: dict) -> Tuple[str, str]:
        """
        Abstract method to create cloud-native Terraform remote state storage.

        This method should be implemented by specific cloud provider classes (e.g., AWS, Azure) to create
        and configure storage resources suitable for managing Terraform's remote state.

        Args:
            name (str): Base name to use for generating the storage resource name.
            **kwargs (dict): Additional keyword arguments specific to the cloud provider's implementation.

        Returns:
            Tuple[str, str]: A tuple containing the identifiers or key information of the created storage resource,
            specific to the cloud provider's implementation.
        """
        pass

    @abstractmethod
    def protect_iac_state_storage(self, name: str, identity: str):
        """
        Restrict access to cloud native terraform remote state storage
        """
        pass

    @abstractmethod
    def destroy_iac_state_storage(self, bucket: str):
        """
        Destroy cloud native terraform remote state storage
        """
        pass

    @abstractmethod
    def create_iac_backend_snippet(self, location: str, service: str, **kwargs: dict) -> str:
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
    def create_autoscaler_snippet(self, cluster_name: str, node_groups: [] = []):
        """
        Creates K8s Autoscaler configuration snippet
        :return: Configuration snippet

        Args:
            cluster_name: K8s cluster name
            node_groups: Node groups definition
        """
        pass

    @abstractmethod
    def create_seal_snippet(self, key_id: str, **kwargs):
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

    @abstractmethod
    def create_ingress_annotations(self) -> str:
        """
        Creates K8s ingress additional annotations
        :return: Annotation definition
        """
        pass

    @abstractmethod
    def create_additional_labels(self) -> str:
        """
        Creates K8s resource additional labels
        :return: Labels definition
        """
        pass

    @abstractmethod
    def create_sidecar_annotation(self) -> str:
        """
        Creates K8s resource sidecar annotation
        :return: Definition
        """
        pass

    @abstractmethod
    def create_external_secrets_config(self, **kwargs) -> str:
        """
        Creates external secrets operator configuration
        :return: External secrets operator configuration
        """
        pass

    @abstractmethod
    def create_iac_pr_automation_config_snippet(self):
        """
        Creates Cloud Provider specific configuration section for Atlantis
        :return: Atlantis configuration section
        """
        pass

    @abstractmethod
    def create_kubecost_annotation(self):
        """
        Creates Cloud Provider specific configuration section for KubeCost
        :return: KubeCost configuration section
        """
        pass

    @abstractmethod
    def create_gpu_operator_parameters(self):
        """
        Creates Cloud Provider specific configuration section for Nvidia GPU operator
        :return: Additional GPU operator parameters
        """
        pass
