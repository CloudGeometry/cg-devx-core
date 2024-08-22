import subprocess
import textwrap
from typing import Optional, Tuple, Any

from common.tracing_decorator import trace
from common.utils.generators import random_string_generator
from common.utils.os_utils import detect_command_presence
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.cloud.gcp.gcp_sdk import GcpSdk
from services.cloud.gcp.iam_permissions import gke_permissions, vpc_permissions, iam_permissions, \
    own_iam_permissions, gcs_project_permissions

CLI = 'gcloud'
K8s = 'kubelogin'


class GcpManager(CloudProviderManager):
    """
    Provides a comprehensive wrapper around Google Cloud Platform (GCP) services.

    This class abstracts the complexities of managing GCP resources, offering methods to handle configurations such
    as DNS deployments, remote state storage protection, and Kubernetes integration.

    Attributes:
        GCLOUD_REQUIRED_COMPONENTS (list[str]): A list of `gcloud` CLI components that are essential for the operation
        of this manager. Currently, it includes:
            - 'gke-gcloud-auth-plugin': Required for authenticating against Google Kubernetes Engine using the gcloud.
    """
    GCLOUD_REQUIRED_COMPONENTS = ['gke-gcloud-auth-plugin']

    def __init__(self, project_id: str, location: Optional[str] = None, bucket_name: Optional[str] = None):
        """
        Initializes the GcpManager instance with the specified project details.

        :param str project_id: The Google Cloud project ID.
        :param Optional[str] location: The location to set for the SDK, defaults to None.
        :param Optional[str] bucket_name: The name of the bucket, defaults to None.
        """
        self.bucket_name: Optional[str] = bucket_name
        self._gcp_sdk = GcpSdk(project_id, location)

    @property
    def region(self) -> str:
        """
        :returns: The location set for the GCP SDK.
        :rtype: str
        """
        return self._gcp_sdk.location

    @property
    def account(self) -> str:
        """
        Retrieves the Google Cloud project ID used in this instance.

        :return: The project ID.
        :rtype: str
        """
        return self._gcp_sdk.project_id

    @trace()
    def protect_iac_state_storage(self, name: str, identity: str) -> None:
        """
        Applies access restrictions to a cloud-native Terraform remote state storage resource based on the specified
        resource name and identity.

        :param str name: The name of the state storage resource to protect.
        :param str identity: The identity (e.g., user or service account) to which the access restrictions will apply.
        """
        self._gcp_sdk.enforce_bucket_security_policy(
            bucket_name=name,
            identities=(identity,)
        )

    @trace()
    def destroy_iac_state_storage(self, bucket: str) -> bool:
        """
        Destroys the specified bucket in Google Cloud Storage.

        :param str bucket: The name of the bucket to destroy.
        :return: True if the bucket was successfully destroyed, False otherwise.
        :rtype: bool
        """
        return self._gcp_sdk.delete_bucket(bucket)

    @trace()
    def create_iac_backend_snippet(self, location: str, service: str, **kwargs: Any) -> str:
        """
        Generates the Terraform backend configuration snippet for a GCP bucket.

        :param str location: The location where the bucket resides.
        :param str service: The service name to use in the Terraform state path.
        :param kwargs: Additional keyword arguments.
        :return: A string containing the Terraform backend configuration.
        :rtype: str
        """
        bucket_name = location or self.bucket_name
        return textwrap.dedent(f'''
              backend "gcs" {{
                bucket  = "{bucket_name}"
                prefix  = "terraform/state/{service}"
            }}''')

    @trace()
    def create_hosting_provider_snippet(self) -> str:
        """
        Creates the Terraform provider configuration snippet for Google Cloud.

        :return: A string containing the Terraform provider configuration.
        :rtype: str
        """
        return textwrap.dedent(f'''
            provider "google" {{
              project = "{self._gcp_sdk.project_id}"
              region  = "{self.region}"
            }}''')

    @trace()
    def create_seal_snippet(self, key_id: str, **kwargs: Any) -> str:
        """
        Generates a Vault configuration snippet using GCP KMS for the seal mechanism.

        :param str key_id: The GCP KMS key identifier.
        :param kwargs: Additional keyword arguments for configuration.
        :return: A string containing the Vault seal configuration.
        :rtype: str
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
        Returns a Kubernetes role mapping identifier specific to Google Cloud.

        :return: A string identifier for the GCP service account role mapping.
        :rtype: str
        """
        return "iam.gke.io/gcp-service-account"

    @trace()
    def get_k8s_auth_command(self) -> tuple[str, [str]]:
        """
        Provides the command to authenticate with a Google Kubernetes Engine (GKE) cluster.

        :return: A tuple containing the command and a list of additional arguments.
        :rtype: tuple[str, [str]]
        """
        args = []
        return 'gke-gcloud-auth-plugin', args

    @trace()
    def get_k8s_token(self, cluster_name: str) -> str:
        """
        Retrieves the access token for authenticating with the specified GKE cluster.

        :param str cluster_name: The name of the GKE cluster.
        :return: The access token.
        :rtype: str
        """
        return self._gcp_sdk.access_token

    @staticmethod
    @trace()
    def detect_cli_presence() -> bool:
        """
        Checks if the gcloud CLI and related Kubernetes components are installed.

        :return: True if all required components are detected, False otherwise.
        :rtype: bool
        """
        return detect_command_presence(CLI) and detect_command_presence(K8s)

    @trace()
    def validate_gcloud_additional_components_installation(self) -> list[str]:
        """
        Checks for the presence of required `gcloud` components and identifies any that are missing.

        :return: A list of strings representing the names of missing required components.
        :rtype: list[str]

        This method checks the installation status of each component in the self.GCLOUD_REQUIRED_COMPONENTS list
        against the list of installed components retrieved from `gcloud`. It returns a list of any components that are not found among the installed ones.
        """
        installed_components = self._get_installed_components()
        return [comp for comp in self.GCLOUD_REQUIRED_COMPONENTS if comp not in installed_components]

    @staticmethod
    @trace()
    def _get_installed_components() -> list[str]:
        """
        Retrieves a list of currently installed `gcloud` components.

        :return: A list of strings representing the IDs of installed `gcloud` components.
        :rtype: list[str]

        This method executes a `gcloud` command to fetch the list of all installed components.
        If the command execution fails, possibly due to `gcloud` not being installed or configured incorrectly,
        an empty list is returned.
        """
        try:
            result = subprocess.run(
                ["gcloud", "components", "list", "--filter=state.name=Installed", "--format=value(id)"],
                text=True, capture_output=True, check=True
            )
            return result.stdout.strip().split('\n')
        except subprocess.CalledProcessError:
            return []

    @trace()
    def create_iac_state_storage(self, name: str, **kwargs: dict) -> tuple[str, str]:
        """
        Creates cloud-native Terraform remote state storage.

        :param str name: The base name for the state storage bucket.
        :param dict kwargs: Additional keyword arguments.
        :return: A tuple containing the bucket name and an empty string since GCP buckets do not have keys.
        :rtype: Tuple[str, str]
        """
        self.bucket_name = f"{name}-{random_string_generator()}".lower()
        self._gcp_sdk.create_bucket(self.bucket_name)

        # Make the bucket private and remove public access
        self._gcp_sdk.set_uniform_bucket_level_access(self.bucket_name)
        self._gcp_sdk.enforce_bucket_security_policy(
            bucket_name=self.bucket_name
        )
        # GCP buckets do not have keys like Azure storage accounts, so we return the bucket name
        return self.bucket_name, ""

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Evaluates if provided credentials have the required permissions across various Google Cloud services.

        :return: True if permissions are sufficient across required services, False otherwise.
        :rtype: bool

        This method assesses permissions for key GCP services like GKE, GCS, VPC, and IAM by checking
        if actions on these services are blocked due to insufficient permissions.
        It compiles a list of missing permissions and evaluates if any are absent.
        """
        missing_permissions = []
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=gke_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=gcs_project_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=vpc_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=iam_permissions))
        missing_permissions.extend(self._gcp_sdk.blocked(permissions=own_iam_permissions))
        return len(missing_permissions) == 0

    @trace()
    def create_ingress_annotations(self) -> str:
        """
        Creates annotations for ingress resources in Google Kubernetes Engine (GKE).

        :return: A string containing YAML-formatted annotations for ingress configurations.
        :rtype: str

        This method generates annotations that configure SSL redirection, connection timeout settings,
        and specify the type of load balancer in GKE environments.
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

        :return: A string containing YAML-formatted labels, empty in this placeholder implementation.
        :rtype: str
        """
        return ""

    @trace()
    def create_sidecar_annotation(self) -> str:
        """
        Creates annotations for sidecar injection in GCP.

        :return: A string containing YAML-formatted sidecar injection annotations, empty in this placeholder implementation.
        :rtype: str
        """
        return ""

    @trace()
    def create_external_secrets_config(self, **kwargs) -> str:
        """
        Creates configuration for external secrets in GCP.

        :param dict kwargs: Additional keyword arguments.
        :return: A string representing the external secrets configuration for GCP.
        :rtype: str

        This method generates a basic configuration indicating that Google Cloud is the provider for external secrets management.
        """
        return "provider: google"

    @trace()
    def create_autoscaler_snippet(self, cluster_name: str, node_groups: Optional[list] = None) -> str:
        """
        GCP natively supports cluster autoscaling without the need for additional configuration snippets.

        :param str cluster_name: The name of the cluster for which autoscaling is enabled.
        :param list node_groups: Optional list of node groups for specific autoscaling rules.
        :return: An empty string, as no snippet is needed for autoscaling in GCP.
        :rtype: str

        Since Google Cloud Platform provides native support for Kubernetes cluster autoscaling,
        this method does not generate any additional configurations.
        """
        return ""

    @trace()
    def create_iac_pr_automation_config_snippet(self):
        """
        Generates the Terraform configuration snippet for infrastructure as code (IaC) pull request automation in GCP.

        :return: A string containing the Terraform configuration snippet for PR automation, empty in this implementation
        :rtype: str
        """
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
        """
        Generates GPU operator configuration parameters for GCP.

        :return: A string representing GPU operator parameters, empty in this implementation.
        :rtype: str
        """
        return ''

    @trace()
    def get_cloud_provider_k8s_dns_deployment_name(self) -> str:
        """
        Retrieves the name of the Kubernetes DNS deployment specific to Google Cloud Platform (GCP).

        :return: A string "kube-dns", indicating the DNS deployment name for GCP.
        :rtype: str
        """
        return "kube-dns"

    def create_ci_artifact_store_config_snippet(self) -> str:
        """
        Creates Cloud Provider specific configuration section for Argo Workflow artifact storage
        :return: Artifact storage configuration section
        """
        return textwrap.dedent('''''')
