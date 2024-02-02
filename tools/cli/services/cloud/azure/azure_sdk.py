import time
import uuid
from typing import List, Tuple, Optional

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, AzureError, ResourceExistsError
from azure.identity import AzureCliCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.dns import DnsManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.v2021_04_01.models import SkuName, Kind
from azure.mgmt.subscription import SubscriptionClient
from azure.storage.blob import BlobServiceClient

from common.logging_config import logger
from services.dns.dns_provider_manager import get_domain_txt_records_dot


class AzureSdk:
    RETRY_COUNT = 100
    RETRY_SLEEP = 10  # in seconds
    RECORD_VALUE = "domain record propagated"

    def __init__(self, subscription_id: str, location: Optional[str] = None):
        self.subscription_id = subscription_id
        self.credential = AzureCliCredential()
        self.authorization_client = AuthorizationManagementClient(self.credential, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.dns_client: DnsManagementClient = DnsManagementClient(self.credential, self.subscription_id)
        self.storage_mgmt_client = StorageManagementClient(self.credential, self.subscription_id)
        self.private_dns_client = PrivateDnsManagementClient(self.credential, self.subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.subscription_client = SubscriptionClient(self.credential)
        self.location = self._validate_location(location)

    def get_name_servers(self, domain_name: str) -> Tuple[List[str], bool, str]:
        """
        Retrieve name servers and resource group name by searching all resource groups in the subscription.

        Args:
        - domain_name (str): Name of the domain.

        Returns:
        - Tuple[List[str], bool, str]: Name servers, is_private flag, and resource_group name.
        """
        try:
            return self._find_domain_name_servers(domain_name)
        except ValueError:
            return [], False, ""
        except HttpResponseError as he:
            logger.error(f"HTTP error occurred: {str(he)}", exc_info=True)
            raise RuntimeError("An HTTP error occurred while fetching domain details") from he

    def _find_domain_name_servers(self, domain_name: str) -> Tuple[List[str], bool, str]:
        """
        Iterate through Azure resource groups to find the specified domain's name servers.

        This method traverses all available resource groups within the Azure subscription,
        utilizing the helper method [_get_name_servers_from_resource_group()] to attempt finding
        the name servers for the specified domain.

        Args:
        - domain_name (str): The domain name for which name servers are being sought.

        Returns:
        Tuple[List[str], bool, str]:
        - A list of name server URLs.
        - A boolean indicating whether the DNS zone is private (True) or public (False).
        - The name of the resource group in which the domain was found.

        Raises:
        - ValueError: If the domain cannot be found in any of the available resource groups.
        """
        for resource_group in self.resource_client.resource_groups.list():
            result = self._get_name_servers_from_resource_group(resource_group.name, domain_name)
            if result:
                return (*result, resource_group.name)
        raise ValueError("Domain not found")

    def _get_name_servers_from_resource_group(
            self, resource_group: str, domain_name: str
    ) -> Optional[Tuple[List[str], bool]]:
        """
        Retrieve the name servers for a specific domain within a specified Azure resource group.

        This method tries to retrieve the domain information from both Public DNS and Private DNS
        within the given resource group. If the domain is found, it returns the name servers and a
        boolean flag indicating whether it's a private DNS zone.

        Args:
        - resource_group (str): The name of the resource group in which to seek the domain.
        - domain_name (str): The domain name for which information is being sought.

        Returns:
        Optional[Tuple[List[str], bool]]:
        - A list of name server URLs, or None if the domain is not found.
        - A boolean indicating whether the DNS zone is private (True) or public (False), or None if the domain is not found.

        Note:
        - If a domain is not found in either the Public DNS or Private DNS of the specified resource group,
          this method returns None.
        - DNS zones might exist in both public and private DNS, depending on your Azure setup.
        """
        # Check Public DNS
        try:
            zone = self.dns_client.zones.get(resource_group, domain_name)
            ns = [f'{z}.' if not z.endswith('.') else z for z in zone.name_servers] if zone.name_servers else []
            return ns, False
        except ResourceNotFoundError:
            pass

        # Check Private DNS
        try:
            zone = self.private_dns_client.private_zones.get(resource_group, domain_name)
            ns = [f'{z}.' if not z.endswith('.') else z for z in zone.name_servers] if zone.name_servers else []
            return ns, True
        except ResourceNotFoundError:
            pass

    def set_hosted_zone_liveness(self, resource_group_name: str, hosted_zone_name: str,
                                 name_servers: List[str]) -> bool:
        """
        Sets a TXT record for liveness check and verifies its propagation.

        Args:
            resource_group_name (str): Name of the Azure resource group.
            hosted_zone_name (str): Name of the DNS hosted zone.
            name_servers (List[str]): List of name servers.

        Returns:
            bool: True if the liveness check passes, else False.
        """
        record_name = f'cgdevx-liveness'

        self._set_txt_record(resource_group_name, hosted_zone_name, record_name, self.RECORD_VALUE)

        is_propagated = self._wait_for_record_propagation(hosted_zone_name, record_name, self.RECORD_VALUE)

        if is_propagated:
            logger.info(f"TXT record for {record_name} propagated successfully.")
        else:
            logger.warning(f"TXT record for {record_name} did not propagate within the expected time.")

        return is_propagated

    def _set_txt_record(self, resource_group_name: str, hosted_zone_name: str, record_name: str, value: str) -> None:
        """
        Ensure a TXT record with the specified value is set in the DNS zone.

        This method will check whether a TXT record with the specified name already exists in the
        given DNS zone.
        If it doesn't, a new TXT record is created with the provided value.

        Args:
        - resource_group_name (str): The name of the Azure resource group where the DNS zone is located.
        - hosted_zone_name (str): The name of the DNS zone where the TXT record will be set.
        - record_name (str): The name of the TXT record to set.
        - value (str): The value to be assigned to the TXT record.

        Returns:
        None

        Raises:
        - azure.core.exceptions.HttpResponseError: If the record cannot be accessed or created for some reason.
        """
        try:
            self.dns_client.record_sets.get(resource_group_name, hosted_zone_name, record_name, 'TXT')
        except ResourceNotFoundError:
            logger.info(f"Creating TXT record {record_name} in {hosted_zone_name}.")
            self.dns_client.record_sets.create_or_update(
                resource_group_name, hosted_zone_name, record_name, 'TXT',
                {'ttl': 10, 'txt_records': [{'value': [value]}]}
            )

    def _get_txt_record(self, resource_group_name: str, hosted_zone_name: str, record_name: str) -> List[str]:
        """
        Retrieve the values of a TXT record from a specified DNS zone.

        Args:
        - resource_group_name (str): The name of the Azure resource group where the DNS zone is located.
        - hosted_zone_name (str): The name of the DNS zone where the TXT record is located.
        - record_name (str): The name of the TXT record to retrieve.

        Returns:
        - List[str]: A list of string values associated with the TXT record.
                      An empty list is returned if the TXT record does not exist.

        Raises:
        - azure.core.exceptions.HttpResponseError: If there is an error accessing the DNS zone or TXT record.
        """
        try:
            record_set = self.dns_client.record_sets.get(resource_group_name, hosted_zone_name, record_name, 'TXT')
            return [record.value for record in record_set.txt_records]
        except ResourceNotFoundError:
            logger.warning(f"TXT record {record_name} not found in {hosted_zone_name}.")
            return []

    def _wait_for_record_propagation(self, hosted_zone_name: str, record_name: str, expected_value: str) -> bool:
        """
        Periodically checks if the TXT record has propagated and its value matches the expected one.

        The method waits and checks repeatedly up to [RETRY_COUNT] times, with a delay of [RETRY_SLEEP]
        seconds between each attempt, for the TXT record to attain the expected value across the DNS
        servers.

        Args:
        - hosted_zone_name (str): The name of the DNS hosted zone.
        - record_name (str): The name of the TXT record to check.
        - expected_value (str): The value that the TXT record should contain.

        Returns:
        bool:
            - True if the expected value is found within the time frame.
            - False otherwise.
        """
        for _ in range(self.RETRY_COUNT):
            time.sleep(self.RETRY_SLEEP)
            existing_txt_records = get_domain_txt_records_dot(f'{record_name}.{hosted_zone_name}')

            if any(expected_value in txt_record for txt_record in existing_txt_records):
                return True

            logger.info(f"Waiting for {record_name} to propagate. Retrying...")

        return False

    def list_user_roles(self) -> [str]:
        """
        Retrieve the list of roles assigned to the authenticated user within the current subscription context.

        This method fetches the role assignments for the authenticated user using the `role_assignments.list_for_subscription`
        method. It filters the assignments to those that are applicable at the current scope level.
        For each role assignment found, it fetches the detailed role definition to extract the role's name.

        Returns:
            [str]: A list of role names assigned to the authenticated user.
                       The list may be empty if the user has no roles assigned in the current subscription scope.

        Raises:
            Any exceptions raised by the Azure SDK's `role_assignments` or `role_definitions` methods will
            propagate up to the caller. This may include API errors, connection issues, or misconfiguration.
        """
        roles = []
        role_assignments = self.authorization_client.role_assignments.list_for_subscription(filter="atScope()")
        for assignment in role_assignments:
            role_definition = self.authorization_client.role_definitions.get_by_id(assignment.role_definition_id)
            roles.append(role_definition.role_name)
        return roles

    def get_role_permissions(self, role_name: str) -> [str]:
        """
        Retrieve permissions associated with a specific role.

        Args:
        - role_name (str): Name of the role to fetch permissions for.

        Returns:
        - [str]: List of permissions associated with the role.
        """
        permissions_list = []
        role_definitions = self.authorization_client.role_definitions.list(
            scope=f'/subscriptions/{self.subscription_id}')
        for role_definition in role_definitions:
            if role_definition.role_name == role_name:
                for permission in role_definition.permissions:
                    permissions_list.extend(permission.actions + permission.not_actions)
                break
        return permissions_list

    def get_subscription_permissions(self) -> [str]:
        """
        Retrieve all permissions at the subscription level.

        Returns:
        - [str]: List of permissions at the subscription level.
        """
        subscription_permissions = []
        subscription_roles = self.list_subscription_roles()
        for role in subscription_roles:
            subscription_permissions.extend(self.get_role_permissions(role))
        return subscription_permissions

    @staticmethod
    def has_permission(user_permissions: [str], required_permission: str) -> bool:
        """
        Check if the provided permissions include the required permission.

        Args:
        - user_permissions ([str]): List of permissions associated with the user.
        - required_permission (str): The permission to check for.

        Returns:
        - bool: True if required_permission is included in user_permissions, else False.
        """
        if '*' in user_permissions:
            return True
        levels = required_permission.split("/")
        for i in range(1, len(levels) + 1):
            if "/".join(levels[:i]) + "/*" in user_permissions:
                return True
        return required_permission in user_permissions

    def list_subscription_roles(self) -> [str]:
        """
        Retrieve the list of roles at the subscription level.

        Returns:
        - [str]: List of roles at the subscription level.
        """
        roles = []
        role_assignments = self.authorization_client.role_assignments.list_for_subscription()
        for assignment in role_assignments:
            role_definition = self.authorization_client.role_definitions.get_by_id(assignment.role_definition_id)
            roles.append(role_definition.role_name)
        return roles

    def blocked(self, required_permissions: [str]) -> [str]:
        """
        Check if the subscription has all the required permissions.

        Args:
        - required_permissions ([str]): List of permissions to check for.

        Returns:
        - [str]: List of missing permissions.
        """
        subscription_permissions = self.get_subscription_permissions()
        return [
            permission for permission in required_permissions if not self.has_permission(
                user_permissions=subscription_permissions,
                required_permission=permission
            )
        ]

    def create_resource_group(self, resource_group_name: str) -> None:
        """
        Create or update an Azure resource group.

        Args:
            resource_group_name (str): The name of the resource group to create or update.
            location (str, optional): The Azure location where the resource group will be hosted.

        Returns:
            None

        Raises:
            AzureError: If there's an error creating or updating the resource group.
        """
        try:
            self.resource_client.resource_groups.create_or_update(resource_group_name, {"location": self.location})
            logger.info(f"Provisioned resource group {resource_group_name} in {self.location}")
        except AzureError as ae:
            logger.error(f"Error provisioning resource group {resource_group_name} in {self.location}: {ae}")
            raise

    def create_storage_account(self, resource_group_name: str, storage_account_name: str) -> None:
        """
        Create a new storage account in the specified resource group and region.

        Args:
            resource_group_name (str): The name of the resource group.
            storage_account_name (str): The desired name for the storage account.
            region (str): The Azure region where the storage account will be created.
        """
        creation_properties = {
            "location": self.location,
            "kind": Kind.STORAGE_V2,
            "sku": {"name": SkuName.STANDARD_LRS}
        }

        try:
            poller = self.storage_mgmt_client.storage_accounts.begin_create(
                resource_group_name, storage_account_name, creation_properties
            )
            account_result = poller.result()
            logger.info(f"Provisioned storage account {account_result.name}")

        except ResourceExistsError:
            logger.warning(f"Storage name {storage_account_name} is already in use. Try another name.")

    def get_storage_account_keys(self, resource_group_name: str, storage_account_name: str):
        """
        Retrieves the access keys for a specified Azure storage account within a given resource group.

        This method calls the Azure Storage Management client to list the keys associated with the storage account.
        These keys are used for authentication and authorization purposes when accessing the storage account.

        Args:
            resource_group_name (str): The name of the resource group containing the storage account.
            storage_account_name (str): The name of the storage account for which keys are being retrieved.

        Returns:
            list: A list of keys for the specified storage account. Typically includes two keys: the primary key and
                  the secondary key. These keys are used for accessing and managing the storage account.

        Note:
            It's crucial to handle these keys securely as they provide full access to the storage account.
            Misuse or unauthorized disclosure of these keys can lead to unauthorized access and potential data breaches.
        """
        r = self.storage_mgmt_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
        return r.keys

    def set_storage_account_versioning(self, storage_account_name: str, resource_group_name: str) -> None:
        """
        Set a storage account data protection options.
        """
        try:
            self.storage_mgmt_client.blob_services.set_service_properties(resource_group_name, storage_account_name,
                                                                          {
                                                                              "is_versioning_enabled": True,
                                                                              "delete_retention_policy": {
                                                                                  "additional_properties": {},
                                                                                  "enabled": True,
                                                                                  "days": 7,
                                                                                  "allow_permanent_delete": False
                                                                              }
                                                                          })
        except Exception as e:
            logger.warning(f"Error while setting blob storage versioning {e}")

        logger.info(f"Set storage account {storage_account_name} data versioning options")

    def set_storage_access(self, identity: str, storage_account_name: str, resource_group_name: str):
        scope = f"subscriptions/{self.subscription_id}/resourcegroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
        response = self.authorization_client.role_assignments.create(scope,
                                                                     uuid.uuid4(),
                                                                     {
                                                                         # Storage Blob Data Owner
                                                                         "role_definition_id": "/providers/Microsoft.Authorization/roleDefinitions/b7e6dc6d-f1e8-4753-8033-0f276bb0955b",
                                                                         "principal_id": identity,
                                                                         "principalType": "ServicePrincipal"
                                                                     })
        return response

    def create_blob_container(self, storage_account_name: str, container_name: str) -> None:
        """Create a blob container in the specified storage account.

        Args:
            storage_account_name (str): The name of the storage account.
            container_name (str): The desired name for the blob container.
        """
        blob_service_client = BlobServiceClient(
            account_url=self._get_account_url(storage_account_name),
            credential=self.credential
        )
        try:
            blob_service_client.create_container(container_name)
            logger.info(f"Blob container '{container_name}' created in storage account '{storage_account_name}'.")
        except ResourceExistsError:
            logger.warning(
                f"Blob container '{container_name}' already exists in storage account '{storage_account_name}'.")

    def create_storage(self, container_name: str, storage_account_name: str, resource_group_name: str) -> None:
        """
        Create storage resources including a resource group, a storage account, and a blob container.

        Args:
            container_name (str): The desired name for the blob container.
            storage_account_name (str): The desired name for the storage account.
            resource_group_name (str): The desired name for the resource group.

        """
        self.create_resource_group(resource_group_name)
        self.create_storage_account(resource_group_name, storage_account_name)
        self.create_blob_container(storage_account_name, container_name)


    def _validate_location(self, location: Optional[str]) -> str:
        """Validate if the provided Azure location is valid. If not, return 'centralus'.

        Args:
            location (str): The Azure location to validate.

        Returns:
            str: The validated Azure location or 'centralus' if provided location is invalid.
        """
        valid_locations = [loc.name for loc in
                           self.subscription_client.subscriptions.list_locations(self.subscription_id)]

        if location and location.lower() in valid_locations:
            return location
        else:
            return 'centralus'

    def destroy_resource_group(self, resource_group_name: str) -> bool:
        """
        Destroy a resource group along with all its resources.

        This function triggers an asynchronous deletion of the specified resource group,
        including all resources contained within it. It waits for the deletion process to complete and logs the result.
        If an error occurs during the deletion process, it is logged, and the function returns False.

        Args:
            resource_group_name (str): The name of the resource group to destroy.

        Returns:
            bool: True if the resource group was successfully destroyed, False otherwise.

        Raises:
            AzureError: If there's an error during the deletion process.
        """
        try:
            # Asynchronous deletion of a resource group. This includes all resources within the group.
            poller = self.resource_client.resource_groups.begin_delete(resource_group_name)

            # Optionally, wait for the deletion to complete
            result = poller.result()  # This will block until deletion completes

            logger.info(f"Resource group {resource_group_name} and all its resources have been deleted.")
        except AzureError as ae:
            logger.error(f"Error deleting resource group {resource_group_name}: {ae}")
            return False
        else:
            return True

    @staticmethod
    def _get_account_url(storage_account_name: str) -> str:
        """Generate the account URL for the given storage account name.

        Args:
            storage_account_name (str): The name of the storage account.

        Returns:
            str: The generated account URL.
        """
        return f'https://{storage_account_name}.blob.core.windows.net'

    def get_tenant_id(self) -> str:
        """Get tenant id.

        Returns:
            str: The tenant id.
        """
        for tenant in self.subscription_client.tenants.list():
            return tenant.tenant_id

    def get_vmss(self, rg_name):
        vmss_list = self.compute_client.virtual_machine_scale_sets.list(rg_name)
        return [v.name for v in vmss_list]
