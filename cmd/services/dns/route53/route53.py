from cmd.services.cloud.aws.aws_manager import AwsSdk
from cmd.services.dns.dns_provider_manager import DNSManager


class Route53Manager(DNSManager):
    __route53_permissions: [str] = ["route53:ListHostedZones",
                                    "route53:ListResourceRecordSets",
                                    "route53:ListTagsForResource"]

    def __init__(self, profile=None, key=None, secret=None):
        self.__aws_sdk = AwsSdk(None, profile, key, secret)

    def evaluate_domain_ownership(self, domain_name):
        """
        Check if domain is owned by user
        :return: True or False
        """
        name_severs = self.__aws_sdk.get_name_severs(domain_name)
        if name_severs is not None:
            self.get_domain_ns_records(domain_name, name_severs)

        self.__aws_sdk.check_hosted_zone_liveness()

    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
            """
        missing_permissions = []
        missing_permissions.extend(self.__aws_sdk.blocked(self.__route53_permissions))
        missing_permissions.extend(
            self.__aws_sdk.blocked(["route53:ChangeResourceRecordSets"], ["arn:aws:route53:::hostedzone/*"]))
        if len(missing_permissions) == 0:
            return True
        else:
            return False
