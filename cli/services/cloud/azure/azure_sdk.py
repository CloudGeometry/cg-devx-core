from typing import List, Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import AzureCliCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.dns import DnsManagementClient


class AzureSdk:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = AzureCliCredential()
        self.client = AuthorizationManagementClient(self.credential, self.subscription_id)

    def get_name_servers(self, resource_group: str, domain_name: str) -> Tuple[List[str], str]:
        """
        Retrieve name servers, etag, and determine if the domain is private.

        Args:
        - resource_group (str): Name of the Azure resource group.
        - domain_name (str): Name of the domain.

        Returns:
        - Tuple[[str], str, bool]: Name servers, etag, and private domain flag.
        """
        try:
            dns_client = DnsManagementClient(self.credential, self.subscription_id)
            zone = dns_client.zones.get(resource_group, domain_name)
        except ResourceNotFoundError:
            raise ValueError("Domain not found") from None
        except Exception as e:
            raise RuntimeError("An unexpected error occurred while fetching domain details") from e

        ns = [f'{z}.' if not z.endswith('.') else z for z in zone.name_servers] if zone.name_servers else []

        return ns, zone.etag

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
        role_assignments = self.client.role_assignments.list_for_subscription(filter="atScope()")
        for assignment in role_assignments:
            role_definition = self.client.role_definitions.get_by_id(assignment.role_definition_id)
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
        role_definitions = self.client.role_definitions.list(scope=f"/subscriptions/{self.subscription_id}")
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
        role_assignments = self.client.role_assignments.list_for_subscription()
        for assignment in role_assignments:
            role_definition = self.client.role_definitions.get_by_id(assignment.role_definition_id)
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
        # ToDo: Need to check personal user permissions, AD permissions or subscription permissions by permission type
        subscription_permissions = self.get_subscription_permissions()
        return [
            permission for permission in required_permissions if not self.has_permission(
                user_permissions=subscription_permissions,
                required_permission=permission
            )
        ]
