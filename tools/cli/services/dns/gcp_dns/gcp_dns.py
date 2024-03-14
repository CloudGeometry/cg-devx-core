from common.tracing_decorator import trace
from services.cloud.gcp.gcp_sdk import GcpSdk
from services.dns.dns_provider_manager import DNSManager, get_domain_ns_records


class GcpDnsManager(DNSManager):
    __dns_permissions: [str] = [
        "dns.managedZones.list",
        "dns.resourceRecordSets.list",
        "dns.resourceRecordSets.create"
    ]

    def __init__(self, project_id: str):
        self.__gcp_sdk = GcpSdk(project_id)

    @trace()
    def evaluate_domain_ownership(self, domain_name: str):
        """
        Check if the domain is owned by the user and create a liveness check record.
        :return: True if the domain is owned and the record is created, False otherwise.
        """
        name_servers, zone_name, _ = self.__gcp_sdk.get_name_servers(domain_name)
        if name_servers and set(get_domain_ns_records(domain_name)).issubset(set(name_servers)):
            return self.__gcp_sdk.set_hosted_zone_liveness(zone_name=zone_name)
        else:
            return False


    @trace()
    def get_domain_zone(self, domain_name: str) -> tuple[str, bool]:
        """
        Retrieve the DNS zone information for a domain.
        :return: Tuple containing the zone ID and a boolean indicating if the zone is private.
        """
        _, zone_name, is_private = self.__gcp_sdk.get_name_servers(domain_name)
        return zone_name, is_private

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Check if provided credentials have required permissions.
        :return: True if permissions are sufficient, False otherwise.
        """
        missing_permissions = []
        missing_permissions.extend(self.__gcp_sdk.blocked(permissions=self.__dns_permissions))
        return len(missing_permissions) == 0
