import textwrap
from typing import Optional, Tuple

from common.enums.gcp_resource_types import GcpResourceType
from common.tracing_decorator import trace
from common.utils.generators import random_string_generator
from common.utils.os_utils import detect_command_presence
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.cloud.gcp.gcp_sdk import GcpSdk
from services.cloud.gcp.iam_permissions import gke_permissions, vpc_permissions, iam_permissions, \
    own_iam_permissions, gcs_project_permissions, gcs_bucket_permissions

CLI = 'gcloud'
K8s = 'kubelogin'


class GcpManager(CloudProviderManager):
    """GCP wrapper."""

    def __init__(self, project_id: str, location: Optional[str] = None, bucket_name: Optional[str] = None):
        self.bucket_name: Optional[str] = bucket_name
        self._gcp_sdk = GcpSdk(project_id, location)

    @property
    def region(self):
        return self._gcp_sdk.location

    @property
    def account(self) -> str:
        """AWS account id"""
        return self._gcp_sdk.project_id

    @trace()
    def protect_iac_state_storage(self, name: str, identity: str):
        """
        Restrict access to cloud native terraform remote state storage
        """
        pass

    @trace()
    def destroy_iac_state_storage(self, bucket: str) -> bool:
        """Destroys the specified bucket."""
        return self._gcp_sdk.delete_bucket(bucket)

    @trace()
    def create_iac_backend_snippet(self, location: str, service: str, **kwargs) -> str:
        """Generates the Terraform backend configuration for GCP."""
        bucket_name = location or self.bucket_name
        return textwrap.dedent(f'''
              backend "gcs" {{
                bucket  = "{bucket_name}"
                prefix  = "terraform/state/{service}"
            }}''')

    @trace()
    def create_hosting_provider_snippet(self):
        """Creates the provider snippet for Terraform configurations."""
        return textwrap.dedent(f'''
            provider "google" {{
              project = "{self._gcp_sdk.project_id}"
              region  = "{self.region}"
            }}''')

    @trace()
    def create_seal_snippet(self, key_id: str, **kwargs) -> str:
        """
        Generates a snippet for configuring Vault's seal with GCP KMS.
        """
        return textwrap.dedent(
            f'''seal "gcpckms" {{
                    project     = "{self._gcp_sdk.project_id}"
                    region      = "global"
                    key_ring    = "{kwargs['key_ring']}"
                    crypto_key  = "{key_id}"
                }}'''
        )

    @trace()
    def create_k8s_cluster_role_mapping_snippet(self) -> str:
        """
        Returns a snippet for Kubernetes cluster role mapping in GCP.
        """
        return "iam.gke.io/gcp-service-account"

    @trace()
    def get_k8s_auth_command(self) -> tuple[str, [str]]:
        """
        Provides the command to authenticate with a GKE cluster.
        """
        args = []
        return 'gke-gcloud-auth-plugin', args

    @trace()
    def get_k8s_token(self, cluster_name: str) -> str:
        """
        Retrieves the access token for the GKE cluster.
        """
        return self._gcp_sdk.access_token

    @staticmethod
    @trace()
    def detect_cli_presence() -> bool:
        """Checks if the gcloud CLI is installed."""
        return detect_command_presence(CLI) and detect_command_presence(K8s)

    @trace()
    def create_iac_state_storage(self, name: str, **kwargs: dict) -> Tuple[str, str]:
        """
        Creates cloud-native Terraform remote state storage.
        """
        self.bucket_name = f"{name}-{random_string_generator()}".lower()
        self._gcp_sdk.create_bucket(self.bucket_name)
        # GCP buckets do not have keys like Azure storage accounts, so we return the bucket name
        return self.bucket_name, ""

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions.
        :return: True if permissions are sufficient, False otherwise.
        """
        missing_permissions = []
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=gke_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=gcs_project_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(
            permissions=gcs_bucket_permissions,
            resource='cgdevx-test-bucket',
            resource_type=GcpResourceType.BUCKET
        ))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=vpc_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=iam_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=own_iam_permissions))
        return len(missing_permissions) == 0

    @trace()
    def create_ingress_annotations(self) -> str:
        """
        Creates annotations for ingress in GKE.
        """
        return textwrap.dedent(
            '''nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
              nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
              cloud.google.com/load-balancer-type: "External"'''
        )

    @trace()
    def create_additional_labels(self) -> str:
        """
        Creates additional labels for Kubernetes resources in GCP.
        """
        return ""

    @trace()
    def create_sidecar_annotation(self) -> str:
        """
        Creates annotations for sidecar injection in GCP.
        """
        return ""

    @trace()
    def create_external_secrets_config(self, **kwargs) -> str:
        """
        Creates configuration for external secrets in GCP.
        """
        return "provider: google"

    @trace()
    def create_autoscaler_snippet(self, cluster_name: str, node_groups=[]):
        """
        GCP-specific implementation will go here.
        """
        return ""

    @trace()
    def create_iac_pr_automation_config_snippet(self):
        """Generates the Terraform configuration snippet for GCP."""
        return ""

    @trace()
    def create_kubecost_annotation(self):
        """
        Creates Cloud Provider specific configuration section for KubeCost
        :return: KubeCost configuration section
        """
        return textwrap.dedent('''
            google-cloud-platform: true
        ''')

    @trace()
    def create_gpu_operator_parameters(self):
        return ''
