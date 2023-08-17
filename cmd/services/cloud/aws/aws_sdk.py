import logging
from typing import Dict, List, Optional

from botocore.exceptions import ClientError

from cmd.services.cloud.aws.aws_session_manager import AwsSessionManager


class AwsSdk:
    def __init__(self, region, profile, key, secret):
        self._session_manager = AwsSessionManager()
        self._session_manager.create_session(region, profile, key, secret)

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
                region = self._session_manager.session.region_name

            s3_client = self._session_manager.session.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_name_severs(self, domain_name: str):
        r53_client = self._session_manager.session.client('route53')
        hosted_zones = r53_client.list_hosted_zones()
        z = next(zone for zone in hosted_zones["HostedZones"] if zone["Name"].find(domain_name))
        zone_id = z["Id"]
        hosted_zone = r53_client.get_hosted_zone(Id=zone_id)
        if hosted_zone["Config"]["PrivateZone"]:
            return None

        return hosted_zone["DelegationSet"]["NameServers"]

    def check_hosted_zone_liveness(self, domain_name):
        pass


# TODO:rewrite code below
"""

// TestHostedZoneLiveness checks Route53 for the liveness test record
func (conf *AWSConfiguration) TestHostedZoneLiveness(hostedZoneName string) bool {
	route53RecordName := fmt.Sprintf("kubefirst-liveness.%s", hostedZoneName)
	route53RecordValue := "domain record propagated"

	route53Client := route53.NewFromConfig(conf.Config)

	hostedZoneID, err := conf.GetHostedZoneID(hostedZoneName)
	if err != nil {
		log.Error().Msg(err.Error())
		return false
	}

	log.Info().Msgf("checking to see if record %s exists", route53RecordName)
	log.Info().Msgf("hostedZoneId %s", hostedZoneID)
	log.Info().Msgf("route53RecordName %s", route53RecordName)

	// check for existing record
	records, err := route53Client.ListResourceRecordSets(context.Background(), &route53.ListResourceRecordSetsInput{
		HostedZoneId: aws.String(hostedZoneID),
	})
	if err != nil {
		log.Warn().Msgf("%s", err)
		return false
	}
	for _, r := range records.ResourceRecordSets {
		if *r.Name == fmt.Sprintf("%s.", route53RecordName) {
			log.Info().Msg("domain record found")
			return true
		}
	}

	// create record if it does not exist
	record, err := route53Client.ChangeResourceRecordSets(
		context.Background(),
		&route53.ChangeResourceRecordSetsInput{
			ChangeBatch: &route53Types.ChangeBatch{
				Changes: []route53Types.Change{
					{
						Action: "UPSERT",
						ResourceRecordSet: &route53Types.ResourceRecordSet{
							Name: aws.String(route53RecordName),
							Type: "TXT",
							ResourceRecords: []route53Types.ResourceRecord{
								{
									Value: aws.String(strconv.Quote(route53RecordValue)),
								},
							},
							TTL:           aws.Int64(10),
							Weight:        aws.Int64(100),
							SetIdentifier: aws.String("CREATE liveness check for kubefirst installation"),
						},
					},
				},
				Comment: aws.String("CREATE liveness check for kubefirst installation"),
			},
			HostedZoneId: aws.String(hostedZoneID),
		})
	if err != nil {
		log.Warn().Msgf("%s", err)
		return false
	}
	log.Info().Msgf("record creation status is %s", record.ChangeInfo.Status)

	count := 0
	// todo need to exit after n number of minutes and tell them to check ns records
	// todo this logic sucks
	for count <= 100 {
		count++

		log.Info().Msgf("%s", route53RecordName)
		ips, err := net.LookupTXT(route53RecordName)
		if err != nil {
			ips, err = dns.BackupResolver.LookupTXT(context.Background(), route53RecordName)
		}

		log.Info().Msgf("%s", ips)

		if err != nil {
			log.Warn().Msgf("could not get record name %s - waiting 10 seconds and trying again: \nerror: %s", route53RecordName, err)
			time.Sleep(10 * time.Second)
		} else {
			for _, ip := range ips {
				// todo check ip against route53RecordValue in some capacity so we can pivot the value for testing
				log.Info().Msgf("%s. in TXT record value: %s\n", route53RecordName, ip)
				count = 101
			}
		}
		if count == 100 {
			log.Error().Msg("unable to resolve hosted zone dns record. please check your domain registrar")
			return false
		}
	}
	return true
}
"""
