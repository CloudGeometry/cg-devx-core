from shutil import which

from cmd.services.cloud.aws.s3 import create_bucket
from cmd.services.cloud.cloud_provider_manager import CloudProviderManager

AWS_CLI = 'aws'


class AWSManager(CloudProviderManager):
    """AWS SDK wrapper."""

    def detect_cli_presence(self):
        """Check whether `name` is on PATH and marked as executable."""
        return which(AWS_CLI) is not None

    def create__iac_state_storage(self):
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier
        """
        return create_bucket('bucket', 'region')
