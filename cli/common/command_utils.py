from cli.common.const.parameter_names import CLOUD_REGION, CLOUD_PROFILE, CLOUD_ACCOUNT_ACCESS_KEY, \
    CLOUD_ACCOUNT_ACCESS_SECRET, DNS_REGISTRAR_ACCESS_KEY, DNS_REGISTRAR_ACCESS_SECRET
from cli.common.enums.cloud_providers import CloudProviders
from cli.common.enums.dns_registrars import DnsRegistrars
from cli.common.state_store import StateStore
from cli.services.cloud.aws.aws_manager import AWSManager
from cli.services.cloud.azure.azure_manager import AzureManager
from cli.services.cloud.cloud_provider_manager import CloudProviderManager
from cli.services.dns.dns_provider_manager import DNSManager
from cli.services.dns.route53.route53 import Route53Manager


def init_cloud_provider(state: StateStore):
    cloud_manager = None
    domain_manager = None
    # init proper cloud provider
    if state.cloud_provider == CloudProviders.AWS:
        cloud_manager: CloudProviderManager = AWSManager(state.get_input_param(CLOUD_REGION),
                                                         state.get_input_param(CLOUD_PROFILE),
                                                         state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                                         state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))

        # check if cloud native DNS registrar is selected
        if state.dns_registrar == DnsRegistrars.Route53:
            if state.get_input_param(DNS_REGISTRAR_ACCESS_KEY) is None and state.get_input_param(
                    DNS_REGISTRAR_ACCESS_SECRET) is None:
                # initialise with cloud account permissions
                domain_manager: DNSManager = Route53Manager(profile=state.get_input_param(CLOUD_PROFILE),
                                                            key=state.get_input_param(CLOUD_ACCOUNT_ACCESS_KEY),
                                                            secret=state.get_input_param(CLOUD_ACCOUNT_ACCESS_SECRET))
            else:
                # initialise with provided key and secret
                domain_manager: DNSManager = Route53Manager(
                    key=state.get_input_param(DNS_REGISTRAR_ACCESS_KEY),
                    secret=state.get_input_param(DNS_REGISTRAR_ACCESS_SECRET))
    elif state.cloud_provider == CloudProviders.Azure:
        cloud_manager: AzureManager = AzureManager(state.get_input_param(CLOUD_PROFILE))
    return cloud_manager, domain_manager


