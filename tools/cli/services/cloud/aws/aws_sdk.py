import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from awscli.customizations.eks.get_token import STSClientFactory, TokenGenerator, TOKEN_EXPIRATION_MINS
from botocore.exceptions import ClientError

from common.logging_config import logger
from services.cloud.aws.aws_session_manager import AwsSessionManager
from services.dns.dns_provider_manager import get_domain_txt_records_dot


class AwsSdk:
    RETRY_COUNT = 100
    RETRY_SLEEP = 10  # in seconds

    def __init__(self, region, profile, key, secret):
        self._account_id = None
        self._session_manager = AwsSessionManager()
        self._session_manager.create_session(region, profile, key, secret)

    @property
    def region(self):
        return self._session_manager.session.region_name

    @property
    def account_id(self):
        if self._account_id is None:
            client = self._session_manager.session.client('sts')
            self._account_id = client.get_caller_identity()["Account"]
        return self._account_id

    def current_user_arn(self):
        """Autodetect current user ARN.
        Method doesn't work with STS/assumed roles
        """
        try:
            client = self._session_manager.session.client('iam')
            user = client.get_user()
            return user["User"]["Arn"]

        except ClientError as e:
            logger.error(e)
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

    def create_bucket(self, bucket_name, region=None) -> str:
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default region.

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
            logger.error(e)
            return False
        return bucket_name

    def enable_bucket_versioning(self, bucket_name, region=None):
        if region is None:
            region = self.region

        resource = self._session_manager.session.resource("s3", region_name=region)
        versioning = resource.BucketVersioning(bucket_name)
        versioning.enable()

    def set_bucket_policy(self, bucket_name: str, identity: str, region: str = None):
        if region is None:
            region = self.region

        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                # non-restrictive allow-list
                {
                    "Sid": "RestrictS3Access",
                    "Action": ["s3:*"],
                    "Effect": "Allow",
                    "Principal": "*",
                    "Condition": {
                        "ArnLike": {
                            "aws:PrincipalArn": [
                                self.current_user_arn(),
                                identity,
                                f"arn:aws:iam::{self._account_id}:root"
                            ]
                        }
                    },
                    "Resource": [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"],
                },
                # an explicit deny. this one is self-sufficient
                {
                    "Sid": "ExplicitlyDenyS3Actions",
                    "Action": ["s3:*"],
                    "Effect": "Deny",
                    "Principal": "*",
                    "Condition": {
                        "ArnNotLike": {
                            "aws:PrincipalArn": [
                                self.current_user_arn(),
                                identity,
                                f"arn:aws:iam::{self._account_id}:root"
                            ]
                        }
                    },
                    "Resource": [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"],
                }
            ]
        }

        policy_string = json.dumps(bucket_policy)

        s3_client = self._session_manager.session.client('s3', region_name=region)

        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=policy_string
        )

    def get_name_servers(self, domain_name: str) -> Tuple[List[str], str, bool]:
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

    def set_hosted_zone_liveness(self, hosted_zone_name: str, hosted_zone_id: str, name_servers: List[str]):

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
                                      "SetIdentifier": "CREATE liveness check for CG DevX cluster installation", }}],
                     "Comment": "CREATE liveness check for CG DevX cluster installation"}

            r = r53_client.change_resource_record_sets(HostedZoneId=hosted_zone_id, ChangeBatch=batch)

        for _ in range(self.RETRY_COUNT):
            time.sleep(self.RETRY_SLEEP)
            existing_txt = get_domain_txt_records_dot(route53_record_name)

            if set(existing_txt).issubset(set([f'"{route53_record_value}"'])):
                return True

            logger.info(f"Waiting for {route53_record_value} to propagate. Retrying...")

        return False

    def get_token(self, cluster_name: str, role_arn: str = None) -> dict:
        # hack to get botcore session and properly initialise client factory
        client_factory = STSClientFactory(self._session_manager.session._session)
        sts_client = client_factory.get_sts_client(role_arn=role_arn)
        token = TokenGenerator(sts_client).get_token(cluster_name)
        return {
            "kind": "ExecCredential",
            "apiVersion": "client.authentication.k8s.io/v1alpha1",
            "spec": {},
            "status": {
                "expirationTimestamp": self._get_expiration_time(),
                "token": token
            }
        }

    @staticmethod
    def _get_expiration_time():
        token_expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINS)
        return token_expiration.strftime('%Y-%m-%dT%H:%M:%SZ')

    def delete_bucket(self, bucket_name: str, region: str = None):
        """Deletes an S3 bucket with all content in a specified region

         If a region is not specified, the bucket is created in the S3 default region.

         :param bucket_name: Bucket to create
         :param region: Region to create bucket in, e.g., 'us-west-2'
         :return: True if bucket deleted, else False
         """

        # Delete bucket and all content
        try:
            if region is None:
                region = self.region

            resource = self._session_manager.session.resource("s3", region_name=region)
            s3_client = self._session_manager.session.client("s3", region_name=region)

            bucket = resource.Bucket(bucket_name)
            bucket_versioning = resource.BucketVersioning(bucket_name)

            if bucket_versioning.status == 'Enabled':
                bucket.object_versions.delete()
            else:
                bucket.objects.all().delete()

            s3_client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True
