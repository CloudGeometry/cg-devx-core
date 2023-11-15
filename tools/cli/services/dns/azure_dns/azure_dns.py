from common.tracing_decorator import trace
from services.cloud.azure.azure_sdk import AzureSdk
from services.dns.dns_provider_manager import DNSManager, get_domain_ns_records


class AzureDNSManager(DNSManager):
    __azure_dns_permissions: [str] = ["Microsoft.Network/dnszones/read",
                                      "Microsoft.Network/dnszones/write",
                                      "Microsoft.Network/dnszones/delete"]

    def __init__(self, subscription_id: str):
        self.__azure_sdk = AzureSdk(subscription_id=subscription_id)

    @trace()
    def evaluate_domain_ownership(self, domain_name: str) -> bool:
        """
        Check if domain is owned by user and create liveness check record
        :return: True or False
        """
        name_servers, _, resource_group_name = self.__azure_sdk.get_name_servers(domain_name)
        if name_servers is not None:
            existing_ns = get_domain_ns_records(domain_name)
            if not set(existing_ns).issubset(set(name_servers)):
                return False

        return self.__azure_sdk.set_hosted_zone_liveness(
            resource_group_name=resource_group_name,
            hosted_zone_name=domain_name,
            name_servers=name_servers
        )

    @trace()
    def get_domain_zone(self, domain_name: str) -> tuple[str, bool]:
        name_servers, is_private, resource_group_name = self.__azure_sdk.get_name_servers(domain_name)
        return resource_group_name, is_private

    @trace()
    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
        """
        missing_permissions = []
        missing_permissions.extend(self.__azure_sdk.blocked(self.__azure_dns_permissions))
        return len(missing_permissions) == 0
