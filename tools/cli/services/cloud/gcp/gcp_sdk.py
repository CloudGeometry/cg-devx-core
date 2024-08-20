import time
from typing import List, Optional, Literal, Tuple

from google.auth import default, transport
from google.auth.exceptions import GoogleAuthError
from google.cloud import dns
from google.cloud import exceptions as gcloud_exceptions
from google.cloud import storage
from google.cloud.container_v1 import ClusterManagerClient
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from common.enums.gcp_resource_types import GcpResourceType
from common.logging_config import logger
from services.dns.dns_provider_manager import get_domain_txt_records_dot


class GcpSdk:
    """
    A class providing direct interactions with Google Cloud Platform (GCP) services through its various clients.

    This class abstracts functionalities needed to manage GCP resources like storage, DNS, and Kubernetes clusters,
    making it easier to perform operations such as creating and deleting buckets,
    managing DNS zones, and testing IAM permissions.

    Attributes:
        RETRY_COUNT (int): The number of times to retry a check for DNS record propagation
        RETRY_SLEEP (int): The time interval in seconds between retries for checking DNS record propagation.
        DOMAIN_PROPAGATION_RECORD_VALUE (str): The expected value to check for DNS domain record propagation.
        DEFAULT_RECORD_TTL (int): The default time-to-live in seconds for new DNS records.
        DOMAIN_PROPAGATION_RECORD_NAME (str): The name of the DNS record used to check domain propagation.
    """
    RETRY_COUNT = 100
    RETRY_SLEEP = 10  # in seconds
    DOMAIN_PROPAGATION_RECORD_VALUE = "domain record propagated"
    DEFAULT_RECORD_TTL = 10
    DOMAIN_PROPAGATION_RECORD_NAME = 'cgdevx-liveness'

    def __init__(self, project_id: str, location: Optional[str] = None):
        """
        Initializes a new GcpSdk instance for managing resources within a specific GCP project.

        :param str project_id: The Google Cloud project ID to manage resources within.
        :param Optional[str] location: The default location to manage resources within.
        """
        self.project_id = project_id
        self.location = location
        self.__credentials, _ = default()
        self.storage_client = storage.Client(project=project_id, credentials=self.__credentials)
        self.dns_client = dns.Client(project=project_id, credentials=self.__credentials)
        self.cluster_manager = ClusterManagerClient(credentials=self.__credentials)

    @property
    def access_token(self) -> str:
        """
        Refreshes and retrieves the access token from GCP credentials.

        :return: The current access token.
        :rtype: str
        """
        self.__credentials.refresh(transport.requests.Request())
        return self.__credentials.token

    def retrieve_user_email(self) -> str:
        """
        Retrieves the email address associated with the current OAuth2 user credentials.

        This method attempts to extract the user's email from the OAuth2 credentials using Google's ID token verification process.
        If the credentials are expired or invalid, it will refresh them before proceeding.

        :return: The email address associated with the user credentials.
        :rtype: str
        :raises: GoogleCloudError, ValueError, Exception if unable to retrieve the email.
        """
        try:
            # Refresh credentials if necessary
            self.ensure_credentials_are_valid()

            # Extract and return the email from OAuth2 credentials
            return self.extract_email_from_oauth2_token()

        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to retrieve user email due to Google Cloud error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Value error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while retrieving the user's email: {e}")
            raise

    def identify_principal(self) -> str:
        """
        Identifies and retrieves the principal identity associated with the current session.

        This method determines whether the current credentials are linked to a service account or a user account,
        and returns the corresponding email or identifier. It handles both OAuth2 and service account credentials.

        :return: The email or identifier of the service account or user.
        :rtype: str
        :raises: GoogleCloudError, ValueError, Exception if unable to retrieve the identity.
        """
        try:
            # Ensure credentials are current
            self.ensure_credentials_are_valid()

            # Determine and return the identity based on credential type
            if hasattr(self.__credentials, 'service_account_email'):
                return self.__credentials.service_account_email
            elif hasattr(self.__credentials, 'quota_project_id'):
                return self.retrieve_user_email()
            else:
                raise ValueError("Unable to determine identity from the provided credentials.")
        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to retrieve identity due to Google Cloud error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Value error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while identifying the principal: {e}")
            raise

    def ensure_credentials_are_valid(self):
        """
        Ensures that the current credentials are valid and refreshed.

        This method checks if the credentials are expired or invalid, and refreshes them if necessary.
        It's a critical step before performing any authenticated operations to avoid unauthorized requests.

        :raises: GoogleAuthError, Exception if unable to refresh the credentials.
        """
        try:
            if self.__credentials.token is None or self.__credentials.expired:
                self.__credentials.refresh(transport.requests.Request())
        except GoogleAuthError as e:
            logger.error(f"Failed to refresh credentials: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while refreshing credentials: {e}")
            raise

    def extract_email_from_oauth2_token(self) -> str:
        """
        Extracts the user's email address from the OAuth2 credentials' ID token.

        This method verifies the ID token associated with the OAuth2 credentials and extracts the email address.
        It's specifically designed for handling OAuth2 user credentials.

        :return: The user's email address.
        :rtype: str
        :raises: GoogleAuthError, ValueError, Exception if unable to verify the ID token or extract the email.
        """
        try:
            if isinstance(self.__credentials, Credentials):
                id_info = verify_oauth2_token(
                    self.__credentials.id_token,
                    transport.requests.Request(),
                    self.__credentials.client_id
                )
                return id_info.get('email')
            else:
                raise ValueError("The provided credentials do not include a valid ID token.")
        except GoogleAuthError as e:
            logger.error(f"Failed to verify the ID token and extract the email: {e}")
            raise
        except ValueError as e:
            logger.error(f"Value error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while extracting the email from the ID token: {e}")
            raise

    def create_bucket(self, bucket_name: str, location: Optional[str] = None) -> bool:
        """
        Attempts to create a new storage bucket in the specified or default location.

        :param str bucket_name: The name of the bucket to create.
        :param Optional[str] location: The location in which to create the bucket.
        Falls back to the instance's default location if not specified.
        :return: True if the bucket was successfully created, False if an error occurred.
        :rtype: bool
        """
        final_location = location or self.location
        try:
            bucket = self.storage_client.bucket(bucket_name)
            # Specify location when creating the bucket
            # Fallback to default (multi-regional) if no location specified
            if final_location:
                bucket.create(location=final_location)
            else:
                bucket.create()
            return True
        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to create bucket: {e}")
            return False

    def set_uniform_bucket_level_access(self, bucket_name: str) -> None:
        """
        Enables uniform bucket-level access to ensure the bucket is private.

        :param str bucket_name: The name of the storage bucket to configure.
        """
        try:
            # Retrieve the bucket by name
            bucket = self.storage_client.bucket(bucket_name)

            # Enable uniform bucket-level access
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.update()

            logger.info(f"Uniform bucket-level access enabled for bucket {bucket_name}.")
        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to set uniform bucket-level access for bucket {bucket_name}: {e}")

    def delete_bucket(self, bucket_name: str) -> bool:
        """
        Attempts to delete a specified storage bucket from the GCP project.

        :param str bucket_name: The name of the bucket to delete.
        :return: True if the bucket was successfully deleted, False if an error occurred.
        :rtype: bool
        """
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.delete()
            return True
        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to delete bucket: {e}")
            return False

    def enforce_bucket_security_policy(self, bucket_name: str, identities: tuple[str] = ()) -> None:
        """
        Enforces strict access control policies on the specified GCP storage bucket to ensure that only the
        current user, project owner, and any specified identities have administrative access.

        :param str bucket_name: The name of the storage bucket to secure.
        :param tuple[str] identities: A list of additional service account identities to which the access restrictions
         will apply.
        :return: A status message indicating whether the security policy was successfully applied.
        :rtype: str

        This method configures the IAM policy of the specified bucket to limit access strictly to the current
        authenticated user, project owner, and any additional specified identities. All other access bindings
        are removed, ensuring that only the specified identities can access or modify the bucket's contents.
        This is particularly important for securing sensitive infrastructure-as-code (IaC) state files in
        multi-tenant environments.
        """
        try:
            # Retrieve the current identity (e.g., user email or service account)
            current_identity = self.identify_principal()
            bucket = self.storage_client.bucket(bucket_name)

            # Retrieve the current IAM policy
            policy = bucket.get_iam_policy(requested_policy_version=3)

            # Clear existing bindings
            policy.bindings.clear()

            # Combine the current identity, project owner, and any additional identities into the members set
            members = (
                    {
                        f"user:{current_identity}",
                        f"projectOwner:{self.project_id}"
                    }
                    |
                    {
                        f"serviceAccount:{identity}" for identity in identities
                    }
            )

            # Add the new policy binding
            policy.bindings.append({
                "role": "roles/storage.admin",
                "members": members
            })

            # Update the bucket's IAM policy
            bucket.set_iam_policy(policy)

        except gcloud_exceptions.GoogleCloudError as e:
            logger.error(f"Failed to enforce security policy on the bucket: {e}")
            raise

    def find_zone_by_dns_name(self, dns_name: str) -> Optional[dns.ManagedZone]:
        """
        Find a DNS zone by its DNS name. Uses a substring match to accommodate for the
        trailing dot in fully qualified domain names (FQDNs) used in DNS.

        :param dns_name: The DNS name of the zone to find, with or without the trailing dot.
        :type dns_name: str
        :return: The DNS zone object if found, or None if no such zone exists.
        :rtype: Optional[dns.ManagedZone]

        The trailing dot in a DNS name signifies the root of the DNS hierarchy. Google
        Cloud DNS, following standard DNS practices, includes this dot in the dns_name of
        a zone. Thus, to ensure accurate matching, especially when the provided dns_name
        might not include the trailing dot, a substring match is used.
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

        :param dns_name: The DNS name of the zone to query.
        :type dns_name: str
        :return: A tuple containing the list of name servers, the DNS name, and a boolean indicating the visibility
         status (True for private, False for public).
        :rtype: Tuple[List[str], Optional[str], bool]

        This method first finds the DNS zone by its name. If the zone is found, it fetches the zone's details to
        determine its public or private based on the presence of the 'privateVisibilityConfig' attribute.
        It returns the zone's name servers, DNS name, and visibility status. If the zone is not found or an error
        occurs, it returns an empty list of name servers, None for the DNS name, and False for the visibility status.
        """
        # Initialize the DNS zone object
        zone = self.find_zone_by_dns_name(dns_name)
        if not zone:
            logger.error(f"No zone found with DNS name {dns_name}")
            return [], None, False

        # Determine if the zone is private by checking private attributes
        is_private = zone._properties.get('visibility') == 'private'
        logger.info(f"Zone {zone.name} visibility: {'Private' if is_private else 'Public'}")
        # Return the list of name servers, the DNS name, and the privacy status of the zone
        return zone.name_servers, zone.name, is_private

    def set_hosted_zone_liveness(self, zone_name: str, domain_name: str) -> bool:
        """
        Sets a TXT record for a liveness check and verifies its propagation in a specified DNS zone.

        :param zone_name: The name of the DNS hosted zone where the liveness check will be set.
        :param domain_name: The domain name for which the TXT record is set.
        :type zone_name: str
        :type domain_name: str
        :return: True if the TXT record is successfully propagated, otherwise False.
        :rtype: bool
        """
        try:
            self._set_txt_record(
                zone_name, self.DOMAIN_PROPAGATION_RECORD_NAME, self.DOMAIN_PROPAGATION_RECORD_VALUE, domain_name
            )
        except gcloud_exceptions:
            return False

        is_propagated = self._wait_for_record_propagation(
            domain_name, self.DOMAIN_PROPAGATION_RECORD_NAME, self.DOMAIN_PROPAGATION_RECORD_VALUE
        )
        if is_propagated:
            logger.info(f"TXT record for {self.DOMAIN_PROPAGATION_RECORD_NAME} propagated successfully.")
        else:
            logger.warning(
                f"TXT record for {self.DOMAIN_PROPAGATION_RECORD_NAME} did not propagate within the expected time."
            )
        return is_propagated

    def _set_txt_record(self, zone_name: str, record_name: str, value: str, domain_name: str) -> None:
        """
        Sets a TXT record with a specified value in the DNS zone.

        :param zone_name: The DNS zone where the record will be set.
        :param record_name: The TXT record name.
        :param value: The value assigned to the TXT record.
        :param domain_name: The domain name associated with the record.
        :type zone_name: str
        :type record_name: str
        :type value: str
        :type domain_name: str
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
        Periodically checks for the propagation of a TXT record with a specified value.

        :param domain_name: The domain name associated with the record.
        :param record_name: The TXT record name.
        :param expected_value: The value expected in the TXT record once propagated.
        :type domain_name: str
        :type record_name: str
        :type expected_value: str
        :return: True if the record is found with the expected value within the retry count, otherwise False.
        :rtype: bool
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
        Tests whether the caller has the specified permissions for a given resource or at the project level
        if no specific resource is provided.

        This method uses the Cloud Resource Manager API to check IAM permissions.

        :param permissions: The list of IAM permissions to test.
        :type permissions: List[str]
        :param resource: The specific GCP resource for which to test the permissions, defaults to the project itself.
        :type resource: Optional[str]
        :return: A list of permissions that the caller is granted from the provided list.
        :rtype: List[str]
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
        Tests IAM permissions for a specific GCP storage bucket.

        This method is particularly useful for verifying access controls on bucket resources.

        :param bucket_name: The name of the bucket on which to test permissions.
        :type bucket_name: str
        :param permissions: The list of IAM permissions to check.
        :type permissions: List[str]
        :return: A list of permissions that the caller is granted.
        :rtype: List[str]
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
        Determines which specified permissions are not granted for a resource, based on its type.

        This function is crucial for security operations, ensuring that only authorized actions are permissible on
        critical resources.

        :param permissions: The permissions to check.
        :type permissions: List[str]
        :param resource_type: The type of the resource, either PROJECT or BUCKET. Defaults to PROJECT.
        :type resource_type: Literal[GcpResourceType.PROJECT, GcpResourceType.BUCKET]
        :param resource: The GCP resource for which to check permissions. If not specified, it defaults based on the
        resource type.
        :type resource: Optional[str]
        :return: A list of permissions that are not granted.
        :rtype: List[str]
        """
        if resource_type == GcpResourceType.PROJECT:
            granted_permissions = self.test_iam_permissions(permissions, resource=resource)
        elif resource_type == GcpResourceType.BUCKET and resource:
            granted_permissions = self.test_bucket_iam_permissions(resource, permissions)
        else:
            raise ValueError("Invalid resource type or resource not provided for bucket type.")
        return [perm for perm in permissions if perm not in granted_permissions]
