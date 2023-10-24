from common.const.parameter_names import CLOUD_REGION, CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET
from common.enums.cloud_providers import CloudProviders
from common.enums.dns_registrars import DnsRegistrars
from common.state_store import StateStore
from services.cloud.aws.aws_manager import AWSManager
from services.cloud.azure.azure_manager import AzureManager
from services.cloud.cloud_provider_manager import CloudProviderManager
from services.dns.azure_dns.azure_dns import AzureDNSManager
from services.dns.dns_provider_manager import DNSManager
from services.dns.route53.route53 import Route53Manager


def init_cloud_provider(state: StateStore) -> tuple[CloudProviderManager, DNSManager]:
    cloud_manager: CloudProviderManager = None
    domain_manager: DNSManager = None
    # init proper cloud provider
    if state.cloud_provider == CloudProviders.AWS:
        cloud_manager: AWSManager = AWSManager(state.get_input_param(CLOUD_REGION),
                                               state.get_input_param(CLOUD_PROFILE),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                               state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))

        # check if cloud native DNS registrar is selected
        if state.dns_registrar == DnsRegistrars.Route53:
            if state.get_input_param(DNS_REGISTRAR_ACCESS_KEY) is None and state.get_input_param(
                    DNS_REGISTRAR_ACCESS_SECRET) is None:
                # initialize with cloud account permissions
                domain_manager: DNSManager = Route53Manager(profile=state.get_input_param(CLOUD_PROFILE),
                                                            key=state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                                            secret=state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))
            else:
                # initialize with a provided key and secret
                domain_manager: DNSManager = Route53Manager(
                    key=state.get_input_param(DNS_REGISTRAR_ACCESS_KEY),
                    secret=state.get_input_param(DNS_REGISTRAR_ACCESS_SECRET))

    elif state.cloud_provider == CloudProviders.Azure:
        cloud_manager: AzureManager = AzureManager(
            state.get_input_param(CLOUD_PROFILE), state.get_input_param(CLOUD_REGION)
        )
        domain_manager: DNSManager = AzureDNSManager(state.get_input_param(CLOUD_PROFILE))

    return cloud_manager, domain_manager
