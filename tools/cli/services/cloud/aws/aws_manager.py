import textwrap

from common.utils.generators import random_string_generator
from services.cloud.aws.aws_sdk import AwsSdk
from services.cloud.aws.iam_permissions import vpc_permissions, eks_permissions, s3_permissions, \
    own_iam_permissions, iam_permissions
from services.cloud.cloud_provider_manager import CloudProviderManager
from common.utils.os_utils import detect_command_presence

CLI = 'aws'


class AWSManager(CloudProviderManager):
    """AWS wrapper."""

    def __init__(self, region, profile, key, secret):
        self.__aws_sdk = AwsSdk(region, profile, key, secret)

    @property
    def region(self):
        return self.__aws_sdk.region

    def detect_cli_presence(self) -> bool:
        """Check whether `name` is on PATH and marked as executable."""
        return detect_command_presence(CLI)

    def create_iac_state_storage(self, name: str, **kwargs: dict) -> str:
        """
        Creates cloud native terraform remote state storage
        :return: Resource identifier, Region
        """
        region = self.region
        if kwargs and "region" in kwargs:
            region = kwargs["region"]
        tf_backend_storage_name = f'{name}-{random_string_generator()}'.lower()
        self.__aws_sdk.create_bucket(tf_backend_storage_name, region)
        return tf_backend_storage_name

    def destroy_iac_state_storage(self, bucket: str):
        """
        Destroy cloud native terraform remote state storage
        """
        return self.__aws_sdk.delete_bucket(bucket)

    def create_iac_backend_snippet(self, location: str, service="default", **kwargs: dict):
        # TODO: consider replacing with file template
        region = self.region
        if kwargs and "region" in kwargs:
            region = kwargs["region"]

        return textwrap.dedent('''\
            backend "s3" {{
            bucket = "{bucket}"
            key    = "terraform/{service}/terraform.tfstate"
            region  = "{region}"
            encrypt = true
          }}'''.format(bucket=location, region=region, service=service))

    def create_hosting_provider_snippet(self):
        # TODO: consider replacing with file template
        return textwrap.dedent('''\
        provider "aws" {
          default_tags {
            tags = {
              ClusterName   = local.cluster_name
              ProvisionedBy = "CGDevX"
            }
          }
        }''')

    def create_secret_manager_seal_snippet(self, key_id: str):
        return '''seal "awskms" {{
                  region     = "{region}"
                  kms_key_id = "{kms_key_id}"
                }}'''.format(region=self.region, kms_key_id=key_id)

    def create_k8s_cluster_role_mapping_snippet(self):
        # TODO: consider replacing with file template
        return "eks.amazonaws.com/role-arn"

    def get_k8s_auth_command(self) -> tuple[str, [str]]:
        args = [
            "--region",
            "<CLUSTER_REGION>",
            "eks",
            "get-token",
            "--cluster-name",
            "<CLUSTER_NAME>"
        ]
        return "aws", args

    def get_k8s_token(self, cluster_name: str) -> str:
        token = self.__aws_sdk.get_token(cluster_name=cluster_name)
        return token['status']['token']

    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        missing_permissions = []
        missing_permissions.extend(self.__aws_sdk.blocked(vpc_permissions))
        missing_permissions.extend(self.__aws_sdk.blocked(eks_permissions))
        missing_permissions.extend(self.__aws_sdk.blocked(iam_permissions))
        missing_permissions.extend(self.__aws_sdk.blocked(s3_permissions))
        missing_permissions.extend(self.__aws_sdk.blocked(own_iam_permissions, [self.__aws_sdk.current_user_arn()]))
        return len(missing_permissions) == 0
