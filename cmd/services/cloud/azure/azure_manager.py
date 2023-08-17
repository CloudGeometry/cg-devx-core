from cmd.common.utils.os_utils import detect_command_presence
from cmd.services.cloud.azure.blob_storage import create_storage
from cmd.services.cloud.cloud_provider_manager import CloudProviderManager

CLI = 'az'
K8s = 'kubelogin'


class AzureManager(CloudProviderManager):
    """Azure wrapper."""

    def detect_cli_presence(self):
        """Check whether `name` is on PATH and marked as executable."""
        return detect_command_presence(CLI)

    def create_iac_state_storage(self, bucket, region):
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        return create_storage(bucket, region)
