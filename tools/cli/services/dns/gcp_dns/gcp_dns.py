from common.tracing_decorator import trace
from services.cloud.gcp.gcp_sdk import GcpSdk
from services.dns.dns_provider_manager import DNSManager, get_domain_ns_records


class GcpDnsManager(DNSManager):
    """
    A manager for handling DNS operations specifically on Google Cloud Platform.

    This manager utilizes the GcpSdk to interact with GCP DNS services, providing functionalities to evaluate domain
    ownership, retrieve DNS zone information, and check required DNS permissions.

    :ivar __dns_permissions: List of DNS-related permissions needed to manage DNS configurations.
    """
    __dns_permissions: [str] = [
        "dns.managedZones.list",
        "dns.resourceRecordSets.list",
        "dns.resourceRecordSets.create"
    ]

    def __init__(self, project_id: str):
        """
        Initializes the GcpDnsManager with a specific Google Cloud project ID.

        :param project_id: The Google Cloud project ID.
        :type project_id: str
        """
        self.__gcp_sdk = GcpSdk(project_id)

    @trace()
    def evaluate_domain_ownership(self, domain_name: str):
        """
        Evaluates the ownership of a domain by verifying if the current DNS configuration matches known nameservers.

        :param domain_name: The domain to verify ownership for.
        :type domain_name: str
        :return: True if the domain is owned by the user and a liveness check record is successfully created;
        False otherwise.
        :rtype: bool
        """
        name_servers, zone_name, _ = self.__gcp_sdk.get_name_servers(domain_name)
        if name_servers and set(get_domain_ns_records(domain_name)).issubset(set(name_servers)):
            return self.__gcp_sdk.set_hosted_zone_liveness(zone_name=zone_name, domain_name=domain_name)
        else:
            return False

    @trace()
    def get_domain_zone(self, domain_name: str) -> tuple[str, bool]:
        """
        Retrieves the DNS zone information for a specified domain.

        :param domain_name: The domain for which to retrieve DNS zone information.
        :type domain_name: str
        :return: A tuple containing the zone ID and a boolean indicating if the zone is private.
        :rtype: tuple[str, bool]
        """
        _, zone_name, is_private = self.__gcp_sdk.get_name_servers(domain_name)
        return zone_name, is_private

    @trace()
    def evaluate_permissions(self) -> bool:
        """
        Evaluates if the provided credentials have the required DNS permissions for operations.

        :return: True if all required permissions are granted, False if any are missing.
        :rtype: bool
        """
        missing_permissions = []
        missing_permissions.extend(self.__gcp_sdk.blocked(permissions=self.__dns_permissions))
        return len(missing_permissions) == 0
