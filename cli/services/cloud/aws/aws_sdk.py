import logging
import time
from typing import Dict, List, Optional, Tuple

from botocore.exceptions import ClientError

from cli.services.cloud.aws.aws_session_manager import AwsSessionManager
from cli.services.dns.dns_provider_manager import get_domain_txt_records_doh, get_domain_txt_records_dot


class AwsSdk:
    def __init__(self, region, profile, key, secret):
        self._session_manager = AwsSessionManager()
        self._session_manager.create_session(region, profile, key, secret)

    @property
    def region(self):
        return self._session_manager.session.region_name

    def current_user_arn(self):
        """Autodetect current user ARN.
        Method doesn't work with STS/assumed roles
        """
        try:
            client = self._session_manager.session.client('iam')
            user = client.get_user()
            return user["User"]["Arn"]

        except ClientError as e:
            logging.error(e)
            raise e

    def blocked(self, actions: List[str],
                resources: Optional[List[str]] = None,
                context: Optional[Dict[str, List]] = None
                ) -> List[str]:
        """test whether IAM user is able to use specified AWS action(s)
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/simulate_principal_policy.html

        Args:
            actions (list): AWS action(s) to validate IAM user can use.
            resources (list): Check if action(s) can be used on resource(s).
                If None, action(s) must be usable on all resources ("*").
            context (dict): Check if action(s) can be used with context(s).
                If None, it is expected that no context restrictions were set.

        Returns:
            list: Actions denied by IAM due to insufficient permissions.
        """
        if not actions:
            return []
        actions = list(set(actions))

        if resources is None:
            resources = ["*"]

        _context: List[Dict] = [{}]
        if context is not None:
            # Convert context dict to list[dict] expected by ContextEntries.
            _context = [{
                'ContextKeyName': context_key,
                'ContextKeyValues': [str(val) for val in context_values],
                'ContextKeyType': "string"
            } for context_key, context_values in context.items()]

        iam_client = self._session_manager.session.client('iam')
        results = iam_client.simulate_principal_policy(
            PolicySourceArn=self.current_user_arn(),
            ActionNames=actions,
            ResourceArns=resources,
            ContextEntries=_context
        )['EvaluationResults']

        return sorted([result['EvalActionName'] for result in results
                       if result['EvalDecision'] != "allowed"])

    def create_bucket(self, bucket_name, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        # Create bucket
        try:
            if region is None:
                region = self.region

            s3_client = self._session_manager.session.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            bucket = s3_client.create_bucket(Bucket=bucket_name,
                                             CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return bucket_name, region

    def get_name_severs(self, domain_name: str) -> Tuple[List[str], str, bool]:
        r53_client = self._session_manager.session.client('route53')
        hosted_zones = r53_client.list_hosted_zones()

        hosted_zone = next(filter(lambda x: x["Name"] == f'{domain_name}.', hosted_zones["HostedZones"]), None)
        if hosted_zone is None:
            raise Exception("Domain not found")

        is_private = bool(hosted_zone["Config"]["PrivateZone"])

        zone_id = hosted_zone["Id"]
        hosted_zone = r53_client.get_hosted_zone(Id=zone_id)

        # append . to the record to make if fully-qualified in case it's missing
        ns = []
        for z in hosted_zone["DelegationSet"]["NameServers"]:
            if z.endswith("."):
                ns.append(z)
            else:
                ns.append(f'{z}.')

        return ns, zone_id, is_private

    def set_hosted_zone_liveness(self, hosted_zone_name, hosted_zone_id, name_servers):

        route53_record_name = f'cgdevx-liveness.{hosted_zone_name}'
        route53_record_value = "domain record propagated"

        r53_client = self._session_manager.session.client('route53')
        response = r53_client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        # check if route53RecordName exists in ResourceRecordSets

        record = next(
            filter(lambda x: x["Name"] == route53_record_name and x["Type"] == "TXT", response["ResourceRecordSets"]),
            None)

        # if not - create
        if record is None:
            batch = {"Changes": [{"Action": "UPSERT",
                                  "ResourceRecordSet": {
                                      "Name": route53_record_name,
                                      "Type": "TXT",
                                      "ResourceRecords": [
                                          {
                                              "Value": f'"{route53_record_value}"',
                                          },
                                      ],
                                      "TTL": 10,
                                      "Weight": 100,
                                      "SetIdentifier": "CREATE liveness check for CGDevX cluster installation", }}],
                     "Comment": "CREATE liveness check for CGDevX cluster installation"}

            r = r53_client.change_resource_record_sets(HostedZoneId=hosted_zone_id, ChangeBatch=batch)

        # check if record is updated
        loop_count = 100
        while loop_count > 0:
            time.sleep(10)
            # ["https://" + str(s).rstrip('.') for s in name_servers][0]
            existing_txt = get_domain_txt_records_dot(route53_record_name)

            if set(existing_txt).issubset(set([f'"{route53_record_value}"'])):
                break

            loop_count -= 1

        return True
