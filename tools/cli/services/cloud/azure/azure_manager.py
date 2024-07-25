import textwrap
from typing import Optional, Tuple

from common.tracing_decorator import trace
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

    def __init__(
            self, subscription_id: str, location: Optional[str] = None, storage_container_name: Optional[str] = None
    ):
        self.iac_backend_storage_container_name: Optional[str] = storage_container_name
        self._azure_sdk = AzureSdk(subscription_id, location)

    @property
    def region(self) -> str:
        """Azure geography location"""
        return self._azure_sdk.location

    @property
    def account(self) -> str:
        """Azure tenant id"""
        return self._azure_sdk.get_tenant_id()

    @trace()
    def protect_iac_state_storage(self, name: str, identity: str):
        """
        Restrict access to cloud native terraform remote state storage
        """
        self.iac_backend_storage_container_name = name
        resource_group_name = self._generate_resource_group_name()
        storage_account_name = self._generate_storage_account_name()
        self._azure_sdk.set_storage_access(identity, storage_account_name, resource_group_name)

    @trace()
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
        return self._azure_sdk.destroy_resource_group(self._generate_resource_group_name())

    @trace()
    def create_iac_backend_snippet(self, location: str, service: str, **kwargs) -> str:
        """
        Generate the Terraform configuration for the Azure backend.

        This function creates a text snippet that can be used as the backend configuration in a Terraform file.
        It uses the Azure Resource Manager (azurerm) backend type and includes the resource group name,
        storage account name, and container name, which are generated based on the current class attributes.

        Args:
            location (str): The name of the storage container
            service (str): The name of the service, which is used as part of the key in the backend configuration.

        Returns:
            str: The Terraform backend configuration snippet.
        """
        return textwrap.dedent(f'''\
            backend "azurerm" {{
              resource_group_name  = "{self._generate_resource_group_name(location)}"
              storage_account_name = "{self._generate_storage_account_name(location)}"
              container_name       = "{location or self.iac_backend_storage_container_name}"
              key                  = "terraform/{service}/terraform.tfstate"
            }}''')

    @trace()
    def create_hosting_provider_snippet(self):
        # TODO: consider replacing with file template
        return textwrap.dedent('''\
         provider "azurerm" {
           features {}
         }''')

    @trace()
    def create_seal_snippet(self, key_id: str, **kwargs) -> str:
        if kwargs and "name" in kwargs:
            name = kwargs["name"]
        else:
            raise Exception("Required parameter missing")

        return '''seal "azurekeyvault" {{
                  vault_name     = "{name}-kv"
                  key_name       = "{key_id}"
                }}'''.format(key_id=key_id, name=name)

    @trace()
    def create_k8s_cluster_role_mapping_snippet(self) -> str:
        return "azure.workload.identity/client-id"

    @trace()
    def get_k8s_auth_command(self) -> tuple[str, [str]]:
        raise NotImplementedError()

    @trace()
    def get_k8s_token(self, cluster_name: str) -> str:
        raise NotImplementedError()

    @classmethod
    def detect_cli_presence(cls) -> bool:
        """Check whether dependencies are on PATH and marked as executable."""
        return detect_command_presence(CLI) & detect_command_presence(K8s)

    @trace()
    def create_iac_state_storage(self, name: str, **kwargs: dict) -> Tuple[str, str]:
        """
        Creates cloud-native Terraform remote state storage.

        The method generates a unique name for the storage container based on the provided 'name' and a random
        string. It then creates a resource group and a storage account adhering to Azure's naming conventions.
        After setting up the storage account, it retrieves the storage account keys and enables versioning
        for the storage account.

        Args:
            name (str): Base name to use for generating the storage container name.
            **kwargs (dict): Additional keyword arguments that may be used in the future.

        Returns:
            tuple: A tuple containing the resource identifier of the created storage
            and the primary key of the storage account.
        """
        self.iac_backend_storage_container_name = f"{name}-{random_string_generator()}".lower()

        resource_group_name = self._generate_resource_group_name()
        storage_account_name = self._generate_storage_account_name()
        self._azure_sdk.create_storage(
            container_name=self.iac_backend_storage_container_name,
            storage_account_name=storage_account_name,
            resource_group_name=resource_group_name)

        keys = self._azure_sdk.get_storage_account_keys(resource_group_name, storage_account_name)
        self._azure_sdk.set_storage_account_versioning(storage_account_name, resource_group_name)

        return self.iac_backend_storage_container_name, keys[0].value

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        missing_permissions = []
        missing_permissions.extend(self._azure_sdk.blocked(aks_permissions))
        missing_permissions.extend(self._azure_sdk.blocked(blob_permissions))
        missing_permissions.extend(self._azure_sdk.blocked(vnet_permissions))
        missing_permissions.extend(self._azure_sdk.blocked(rbac_permissions))
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

    def _generate_storage_account_name(self, container_name: Optional[str] = None) -> str:
        """
        Generate a unique storage account name that adheres to Azure's naming conventions.

        Azure's storage account name must be between 3 and 24 characters in length and can only use numbers and lower-case letters.

        Args:
            container_name (Optional[str]): The container name to use for generating the storage account name.
                                            If not provided, the internal variable is used.

        Returns:
            str: A unique storage account name adhering to Azure's naming conventions.
        """
        container_name = container_name or self.iac_backend_storage_container_name
        # Remove disallowed characters as the storage account name can only contain numbers and letters
        safe_name = container_name.replace('_', '').replace('-', '')
        return f"{safe_name[:20]}iac".lower()

    def _generate_resource_group_name(self, container_name: Optional[str] = None) -> str:
        """
        Generate a unique resource group name based on the container name.

        Args:
            container_name (Optional[str]): The container name to use for generating the resource group name.
                                            If not provided, the internal variable is used.

        Returns:
            str: A unique name for the resource group.
        """
        container_name = container_name or self.iac_backend_storage_container_name
        return f"{container_name[:20]}-rg"

    @trace()
    def create_ingress_annotations(self) -> str:
        return 'service.beta.kubernetes.io/azure-load-balancer-health-probe-request-path: "/healthz"'

    @trace()
    def create_additional_labels(self) -> str:
        return 'azure.workload.identity/use: "true"'

    @trace()
    def create_sidecar_annotation(self) -> str:
        return 'azure.workload.identity/inject-proxy-sidecar: "true"'

    @trace()
    def create_external_secrets_config(self, **kwargs) -> str:
        if kwargs and "location" in kwargs:
            location = kwargs["location"]
        else:
            raise Exception("Required parameter missing")

        return '''
        provider: azure
        secretConfiguration:
          enabled: true
          mountPath: "/etc/kubernetes/"
          data:
            azure.json: |
              {{
                "subscriptionId": "{subscription_id}",
                "resourceGroup": "{resource_group}",
                "useWorkloadIdentityExtension": true
              }}'''.format(subscription_id=self._azure_sdk.subscription_id, resource_group=location)

    @trace()
    def create_autoscaler_snippet(self, cluster_name: str, node_groups=[]):
        autoscaling_groups = ""
        vmss_list = self._azure_sdk.get_vmss(f"{cluster_name}-vmss-rg")

        if not len(vmss_list):
            raise Exception("Could not find vmss")

        for node in node_groups:
            vmss_name = [vmss for vmss in vmss_list if vmss.startswith(f'aks-{node["name"]}-')][0]
            autoscaling_groups += f'''
          - name: {vmss_name}
            minSize: {node["min_size"]}
            maxSize: {node["max_size"]}'''

        tenant_id = self._azure_sdk.get_tenant_id()
        return f'''autoscalingGroups: {autoscaling_groups}
        azureClientID: "<CLUSTER_AUTOSCALER_IAM_ROLE_RN>"
        azureResourceGroup: {cluster_name}-vmss-rg
        azureSubscriptionID: {self._azure_sdk.subscription_id}
        azureTenantID: {tenant_id}
        azureUseWorkloadIdentityExtension: true
        azureVMType: "vmss"'''

    @trace()
    def create_iac_pr_automation_config_snippet(self):
        return '''# azure specific section
      ARM_USE_AKS_WORKLOAD_IDENTITY       = true,
      ARM_USE_CLI                         = false,
      ARM_SUBSCRIPTION_ID                 = "<AZ_SUBSCRIPTION_ID>",
      ARM_CLIENT_ID                       = "<IAC_PR_AUTOMATION_IAM_ROLE_RN>",
      ARM_ACCESS_KEY                      = var.tf_backend_storage_access_key,
      # ----'''

    @trace()
    def create_kubecost_annotation(self):
        return '''azure-cloud-services: true'''

    @trace()
    def create_gpu_operator_parameters(self):
      return '''# azure
        - name: "driver.enabled"
          value: "false"
        - name: "toolkit.enabled"
          value: "false"
        - name: "operator.runtimeClass"
          value: "nvidia-container-runtime"'''
