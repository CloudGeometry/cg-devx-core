from common.tracing_decorator import trace
from services.cloud.aws.aws_manager import AwsSdk
from services.dns.dns_provider_manager import DNSManager, get_domain_ns_records


class Route53Manager(DNSManager):
    __route53_permissions: [str] = ["route53:ListHostedZones",
                                    "route53:ListResourceRecordSets",
                                    "route53:ListTagsForResource"]

    def __init__(self, profile=None, key=None, secret=None):
        self.__aws_sdk = AwsSdk(None, profile, key, secret)

    @trace()
    def evaluate_domain_ownership(self, domain_name: str):
        """
        Check if domain is owned by user and create liveness check record
        :return: True or False
        """
        name_servers, zone_id, _ = self.__aws_sdk.get_name_servers(domain_name)
        if name_servers is not None:
            existing_ns = get_domain_ns_records(domain_name)
            if not set(existing_ns).issubset(set(name_servers)):
                return False

        return self.__aws_sdk.set_hosted_zone_liveness(domain_name, zone_id, name_servers)

    @trace()
    def get_domain_zone(self, domain_name: str) -> tuple[str, bool]:
        name_servers, zone_id, is_private = self.__aws_sdk.get_name_servers(domain_name)
        return zone_id, is_private

    @trace()
    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
            """
        missing_permissions = []
        missing_permissions.extend(self.__aws_sdk.blocked(self.__route53_permissions))
        missing_permissions.extend(
            self.__aws_sdk.blocked(["route53:ChangeResourceRecordSets"], ["arn:aws:route53:::hostedzone/*"]))
        return len(missing_permissions) == 0
