import textwrap
from typing import Optional

from common.utils.generators import random_string_generator
from common.utils.os_utils import detect_command_presence
from services.cloud.azure.azure_sdk import AzureSdk
from services.cloud.azure.iam_permissions import aks_permissions, blob_permissions, vnet_permissions, \
    rbac_permissions
from services.cloud.cloud_provider_manager import CloudProviderManager

CLI = 'az'
K8s = 'kubelogin'


class AzureManager(CloudProviderManager):
    """Azure wrapper."""

    def __init__(self, subscription_id: str, location: Optional[str] = None):
        self.iac_backend_storage_container_name: Optional[str] = None
        self.__azure_sdk = AzureSdk(subscription_id, location)

    @property
    def region(self):
        return self.__azure_sdk.location

    def destroy_iac_state_storage(self, bucket: str) -> bool:
        """
        Destroy the cloud-native Terraform remote state storage.

        This function uses the Azure SDK to destroy the resource group associated with the specified bucket.
        The resource group name is generated based on the current class attributes, and the class attribute
        `iac_backend_storage_container_name` is updated with the provided bucket name before generating
         the resource group name.

        Args:
            bucket (str): The name of the bucket associated with the resource group to be destroyed.

        Returns:
            bool: True if the resource group was successfully destroyed, False otherwise.
        """
        self.iac_backend_storage_container_name = bucket
        return self.__azure_sdk.destroy_resource_group(self._generate_resource_group_name())

    def create_iac_backend_snippet(self, service: str = "default", **kwargs) -> str:
        """
        Generate the Terraform configuration for the Azure backend.

        This function creates a text snippet that can be used as the backend configuration in a Terraform file.
        It uses the Azure Resource Manager (azurerm) backend type and includes the resource group name,
        storage account name, and container name, which are generated based on the current class attributes.

        Args:
            service (str): The name of the service, which is used as part of the key in the backend configuration.

        Returns:
            str: The Terraform backend configuration snippet.
        """
        return textwrap.dedent(f'''\
            backend "azurerm" {{
              resource_group_name  = "{self._generate_resource_group_name()}"
              storage_account_name = "{self._generate_storage_account_name()}"
              container_name       = "{self.iac_backend_storage_container_name}"
              key                  = "terraform/{service}/terraform.tfstate"
            }}''')

    def create_hosting_provider_snippet(self):
        # TODO: consider replacing with file template
        return textwrap.dedent('''\
         provider "azurerm" {
           features {}
         }''')

    def create_secret_manager_seal_snippet(self, key_id: str):
        return '''seal "azurekeyvault" {{
                  tenant_id     = "tenant-id"
                  vault_name     = "hc-vault"
                  key_name       = "key-name"
                }}'''

    def create_k8s_cluster_role_mapping_snippet(self):
        return "azure.workload.identity/client-id"

    def get_k8s_auth_command(self) -> tuple[str, [str]]:
        args = [
            "aks"
            "get-credentials"
            "--name",
            "<CLUSTER_NAME>"
            "--resource-group",
            "<CLUSTER_NAME>-rg",
            "--admin",
            "--public-fqdn"
            "true"
        ]
        return "az", args

    def get_k8s_token(self, cluster_name: str) -> str:
        raise NotImplementedError()

    def detect_cli_presence(self):
        """Check whether dependencies are on PATH and marked as executable."""
        return detect_command_presence(CLI) & detect_command_presence(K8s)

    def create_iac_state_storage(self, name: str, **kwargs: dict) -> str:
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        self.iac_backend_storage_container_name = f"{name}-{random_string_generator()}".lower()
        return self.__azure_sdk.create_storage(self.iac_backend_storage_container_name,
                                               self._generate_storage_account_name(),
                                               self._generate_resource_group_name())

    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        missing_permissions = []
        missing_permissions.extend(self.__azure_sdk.blocked(aks_permissions))
        missing_permissions.extend(self.__azure_sdk.blocked(blob_permissions))
        missing_permissions.extend(self.__azure_sdk.blocked(vnet_permissions))
        missing_permissions.extend(self.__azure_sdk.blocked(rbac_permissions))
        return len(missing_permissions) == 0

    @staticmethod
    def _generate_container_name(base_name: str) -> str:
        """
        Generate a unique container name based on the provided base name and a random string.

        Args:
            base_name (str): The base name for the container.

        Returns:
            str: The generated unique container name.
        """
        return f"{base_name}-{random_string_generator()}".lower()

    def _generate_storage_account_name(self) -> str:
        """
        Generate a unique storage account name that adheres to Azure's naming conventions.

        Azure's storage account name must be between 3 and 24 characters in length and can only use numbers and lower-case letters.

        Returns:
            str: A unique storage account name adhering to Azure's naming conventions.
        """
        # Remove characters as storage account name could only contain numbers and letters
        safe_name = self.iac_backend_storage_container_name.replace('_', '').replace('-', '')
        return f"{safe_name[:20]}-iac".lower()

    def _generate_resource_group_name(self) -> str:
        """
        Generate a unique resource group name based on the container name.

        Returns:
            str: A unique name for the resource group.
        """
        return f"rg-{self.iac_backend_storage_container_name[:20]}"
