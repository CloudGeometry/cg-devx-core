import time
from typing import List, Optional, Literal, Tuple

from google.auth import default, transport
from google.cloud import dns
from google.cloud import exceptions as gcloud_exceptions
from google.cloud import storage
from google.cloud.container_v1 import ClusterManagerClient
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from common.enums.gcp_resource_types import GcpResourceType
from common.logging_config import logger
from services.dns.dns_provider_manager import get_domain_txt_records_dot


class GcpSdk:
    RETRY_COUNT = 100
    RETRY_SLEEP = 10  # in seconds
    DOMAIN_PROPAGATION_RECORD_VALUE = "domain record propagated"
    DEFAULT_RECORD_TTL = 10

    def __init__(self, project_id, location=None):
        self.project_id = project_id
        self.location = location
        self.__credentials, _ = default()
        self.storage_client = storage.Client(project=project_id, credentials=self.__credentials)
        self.dns_client = dns.Client(project=project_id, credentials=self.__credentials)
        self.cluster_manager = ClusterManagerClient(credentials=self.__credentials)

    @property
    def access_token(self):
        self.__credentials.refresh(transport.requests.Request())
        return self.__credentials.token

    def create_bucket(self, bucket_name, location=None):
        """Create a new bucket in a specific project and location"""
        final_location = location or self.location
        try:
            bucket = self.storage_client.bucket(bucket_name)
            if final_location:
                bucket.create(location=final_location)  # Specify location when creating the bucket
            else:
                bucket.create()  # Fallback to default (multi-regional) if no location specified
            return True
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            return False

    def delete_bucket(self, bucket_name):
        """Deletes a bucket in a specific project"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete bucket: {e}")
            return False

    def find_zone_by_dns_name(self, dns_name: str) -> Optional[dns.ManagedZone]:
        """
        Find a DNS zone by its DNS name. Uses a substring match to accommodate for the
        trailing dot in fully qualified domain names (FQDNs) used in DNS.

        The trailing dot in a DNS name signifies the root of the DNS hierarchy. Google
        Cloud DNS, following standard DNS practices, includes this dot in the dns_name of
        a zone. Thus, to ensure accurate matching, especially when the provided dns_name
        might not include the trailing dot, a substring match is used.

        Args:
            dns_name (str): The DNS name of the zone to find, with or without the trailing dot.

        Returns:
            Optional[dns.Zone]: The found zone object or None if not found.
        """
        zones = self.dns_client.list_zones()
        for zone in zones:
            # Check if the provided DNS name is a substring of the zone's dns_name
            if dns_name in zone.dns_name:
                return zone
        logger.info(f"No zone found with DNS name {dns_name}")
        return None

    def get_name_servers(self, dns_name: str) -> Tuple[List[str], Optional[str], bool]:
        """
        Retrieves the name servers and visibility status for a DNS zone identified by its DNS name.

        This method first finds the DNS zone by its name. If the zone is found, it fetches the zone's details to determine
        its visibility status (public or private) based on the presence of the 'privateVisibilityConfig' attribute.
        It returns the zone's name servers, DNS name, and visibility status. If the zone is not found or an error occurs,
        it returns an empty list of name servers, None for the DNS name, and False for the visibility status.

        Args:
            dns_name (str): The DNS name of the zone to query.

        Returns:
            Tuple[List[str], Optional[str], bool]: A tuple containing the list of name servers, the DNS name,
            and a boolean indicating the zone's visibility (True for private, False for public).
        """
        # ToDo: Discuss implementation (It can be done without brute force, but need to pass exact zone name)
        # Initialize the DNS zone object
        zone = self.find_zone_by_dns_name(dns_name)
        if not zone:
            logger.error(f"No zone found with DNS name {dns_name}")
            return [], None, False

        # Attempt to load the zone's details
        # try:
        #    managed_zone = zone.reload()  # Fetches the latest zone details from the server
        # except GoogleCloudError as e:
        #    logger.error(f"Failed to get details for zone {dns_name}: {e}")
        #    return [], None, False
        # except NotFound as e:
        #    logger.error(f"Zone not found: {zone_name} - {e}")
        #    return [], None, False

        # Determine if the zone is private by checking private attributes
        is_private = zone._properties.get('visibility') == 'private'
        logger.info(f"Zone {zone.name} visibility: {'Private' if is_private else 'Public'}")
        # Return the list of name servers, the DNS name, and the privacy status of the zone
        return zone.name_servers, zone.name, is_private

    def set_hosted_zone_liveness(self, zone_name: str, domain_name: str) -> bool:
        """
        Sets a TXT record for liveness check and verifies its propagation in a Google Cloud DNS zone.

        Args:
            zone_name (str): The name of the DNS hosted zone.

        Returns:
            bool: True if the liveness check passes, else False.
        """
        record_name = f'cgdevx-liveness'
        try:
            self._set_txt_record(zone_name, record_name, self.DOMAIN_PROPAGATION_RECORD_VALUE, domain_name)
        except gcloud_exceptions:
            return False

        is_propagated = self._wait_for_record_propagation(domain_name, record_name,
                                                          self.DOMAIN_PROPAGATION_RECORD_VALUE)
        if is_propagated:
            logger.info(f"TXT record for {record_name} propagated successfully.")
        else:
            logger.warning(f"TXT record for {record_name} did not propagate within the expected time.")
        return is_propagated

    def _set_txt_record(self, zone_name: str, record_name: str, value: str, domain_name: str) -> None:
        """
        Ensure a TXT record with the specified value is set in the DNS zone.

        Args:
            zone_name (str): The name of the DNS zone where the TXT record will be set.
            record_name (str): The name of the TXT record to set.
            value (str): The value to be assigned to the TXT record.
        """
        try:
            zone = self.dns_client.zone(zone_name)
            # Step 1: Get the record set
            record_set = zone.resource_record_set(
                name=f"{record_name}.{domain_name}.",
                record_type='TXT',
                ttl=self.DEFAULT_RECORD_TTL,
                rrdatas=[f'"{value}"']
            )
        except gcloud_exceptions.NotFound as not_found_exc:
            logger.error(f"Zone {zone_name} or record set not found: {not_found_exc}")
            raise

        try:
            # Step 2: Apply changes to the DNS zone
            changes = zone.changes()
            changes.add_record_set(record_set)
            changes.create()
            logger.info(f"TXT record {record_name} with value {value} has been created in {zone_name}.")
        except gcloud_exceptions.GoogleCloudError as gcloud_err:
            if gcloud_err.code == 409:  # Check if the error code is 409 indicating a conflict
                logger.info(f"TXT record {record_name} already exists in {zone_name}. Skipping creation")
                return
            logger.error(f"An error occurred while applying changes to the DNS zone: {gcloud_err}")
            raise
        except Exception as general_exc:
            logger.error(f"An unexpected error occurred while applying changes to the DNS zone: {general_exc}")
            raise

    def _wait_for_record_propagation(self, domain_name: str, record_name: str, expected_value: str) -> bool:
        """
        Periodically checks if the TXT record has propagated and its value matches the expected one.

        Args:
            hosted_zone_name (str): The name of the DNS hosted zone.
            record_name (str): The name of the TXT record to check.
            expected_value (str): The value that the TXT record should contain.

        Returns:
            bool: True if the expected value is found within the time frame, False otherwise.
        """
        for _ in range(self.RETRY_COUNT):
            time.sleep(self.RETRY_SLEEP)

            existing_txt_records = get_domain_txt_records_dot(f'{record_name}.{domain_name}')

            if any(expected_value in txt_record for txt_record in existing_txt_records):
                return True

            logger.info(f"Waiting for {record_name} to propagate. Retrying...")

        logger.warning(f"TXT record for {record_name} did not propagate within the expected time.")
        return False

    def test_iam_permissions(self, permissions: List[str], resource: Optional[str] = None) -> List[str]:
        """
        Test whether the caller has the specified permissions for a resource or at the project level if no resource is provided.

        Args:
            permissions (list): The permissions to test.
            resource (str, optional): The resource for which to test permissions. Defaults to the project.

        Returns:
            list: Permissions that the caller is granted from the input list.
        """
        if not resource:
            resource = f"{self.project_id}"

        service = discovery.build(
            serviceName='cloudresourcemanager',
            version='v1',
            credentials=self.__credentials
        )
        request_body = {'permissions': permissions}
        try:
            request = service.projects().testIamPermissions(resource=resource, body=request_body)
            response = request.execute()
        except HttpError as error:
            logger.error(f"Failed to test permissions for {resource}: {error}")
            return []

        return response.get('permissions', [])

    def test_bucket_iam_permissions(self, bucket_name: str, permissions: List[str]) -> List[str]:
        """
        Test IAM permissions for a specific bucket.

        Args:
            bucket_name (str): The name of the bucket to test permissions on.
            permissions (List[str]): The permissions to check.

        Returns:
            List[str]: Permissions that the caller is granted.
        """
        bucket = self.storage_client.bucket(bucket_name)
        try:
            response = bucket.test_iam_permissions(permissions)
            return response
        except HttpError as error:
            logger.error(f"Error testing IAM permissions for bucket {bucket_name}: {error}")
            return []

    def blocked(
            self,
            permissions: List[str],
            resource_type: Literal[GcpResourceType.PROJECT, GcpResourceType.BUCKET] = GcpResourceType.PROJECT,
            resource: Optional[str] = None
    ) -> List[str]:
        """
        Determine which of the specified permissions are not granted for a resource, based on the resource type.

        Args:
            permissions (list): The permissions to check.
            resource_type (ResourceTypeLiteral): The type of the resource (PROJECT or BUCKET), default to PROJECT.
            resource (str, optional): The GCP resource for which to check permissions.

        Returns:
            list: Permissions that are not granted to the caller.
        """
        if resource_type == GcpResourceType.PROJECT:
            granted_permissions = self.test_iam_permissions(permissions, resource=resource)
        elif resource_type == GcpResourceType.BUCKET and resource:
            granted_permissions = self.test_bucket_iam_permissions(resource, permissions)
        else:
            raise ValueError("Invalid resource type or resource not provided for bucket type.")
        return [perm for perm in permissions if perm not in granted_permissions]
