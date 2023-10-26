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
        self.iac_backend_resource_group_name = None
        self.iac_backend_storage_account_name = None
        self.__azure_sdk = AzureSdk(subscription_id, location)

    @property
    def region(self):
        return self.__azure_sdk.location

    def destroy_iac_state_storage(self, bucket: str):
        raise NotImplementedError()

    def create_iac_backend_snippet(self, location: str, service: str = "default", **kwargs: dict):
        resource_group = self.iac_backend_resource_group_name
        storage_account = self.iac_backend_storage_account_name

        if kwargs and "resource_group" in kwargs:
            resource_group = kwargs["resource_group"]
        if kwargs and "storage_account" in kwargs:
            storage_account = kwargs["storage_account"]

        return textwrap.dedent('''\
            backend "azurerm" {{
              resource_group_name  = "{resource_group}"
              storage_account_name = "{storage_account}"
              container_name       = "{container_name}"
              key                  = "terraform/{service}/terraform.tfstate"
            }}'''.format(resource_group=resource_group,
                         storage_account=storage_account,
                         container_name=location,
                         service=service))

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

        container_name = f"{name}-{random_string_generator()}".lower()
        if kwargs and "storage_account" in kwargs:
            self.iac_backend_storage_account_name = kwargs["storage_account"]
        else:
            # remove characters as storage account name could only contain numbers and letters
            safe_name = name.replace('_', '').replace('-', '')
            self.iac_backend_storage_account_name = f"{safe_name}{random_string_generator(4)}".lower()

        if kwargs and "resource_group" in kwargs:
            self.iac_backend_resource_group_name = kwargs["resource_group"]
        else:
            self.iac_backend_resource_group_name = f"rg-{self.iac_backend_storage_account_name}-iac-backend".lower()

        return self.__azure_sdk.create_storage(container_name,
                                               self.iac_backend_storage_account_name,
                                               self.iac_backend_resource_group_name)

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
