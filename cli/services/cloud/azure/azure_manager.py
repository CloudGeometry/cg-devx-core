from cli.services.cloud.azure.azure_sdk import AzureSdk
from cli.services.cloud.azure.blob_storage import create_storage
from cli.services.cloud.azure.iam_permissions import aks_permissions, blob_permissions, vnet_permissions, \
    rbac_permissions, ad_permissions, own_ad_permissions
from cli.services.cloud.cloud_provider_manager import CloudProviderManager

CLI = 'az'
K8s = 'kubelogin'


class AzureManager(CloudProviderManager):
    """Azure wrapper."""

    def __init__(self, subscription_id: str):
        self.__azure_sdk = AzureSdk(subscription_id)

    def detect_cli_presence(self, cli: str = CLI):
        """Check whether `name` is on PATH and marked as executable."""
        return super().detect_cli_presence(cli)

    def create_iac_state_storage(self, bucket, region):
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        return create_storage(bucket, region)

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
        missing_permissions.extend(self.__azure_sdk.blocked(ad_permissions))
        missing_permissions.extend(self.__azure_sdk.blocked(own_ad_permissions))
        return len(missing_permissions) == 0
