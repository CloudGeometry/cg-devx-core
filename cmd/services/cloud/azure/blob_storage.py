import os
import random

# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.storage.blob import BlobServiceClient


def create_storage(name, region=None):
    try:

        # Acquire a credential object using CLI-based authentication.
        credential = AzureCliCredential()

        # Retrieve subscription ID from environment variable.
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(credential, subscription_id)

        # Constants we need in multiple places: the resource group name and the region
        # in which we provision resources. You can change these values however you want.
        RESOURCE_GROUP_NAME = "PythonAzureExample-Storage-rg"
        LOCATION = "centralus"

        # Step 1: Provision the resource group.

        rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
                                                                     {"location": LOCATION})

        print(f"Provisioned resource group {rg_result.name}")

        # For details on the previous code, see Example: Provision a resource group
        # at https://docs.microsoft.com/azure/developer/python/azure-sdk-example-resource-group

        # Step 2: Provision the storage account, starting with a management object.

        storage_client = BlobServiceClient(credential, subscription_id)

        # This example uses the CLI profile credentials because we assume the script
        # is being used to provision the resource in the same way the Azure CLI would be used.

        STORAGE_ACCOUNT_NAME = f"pythonazurestorage{random.randint(1, 100000):05}"

        # You can replace the storage account here with any unique name. A random number is used
        # by default, but note that the name changes every time you run this script.
        # The name must be 3-24 lower case letters and numbers only.

        # Check if the account name is available. Storage account names must be unique across
        # Azure because they're used in URLs.
        availability_result = storage_client.storage_accounts.check_name_availability(
            {"name": STORAGE_ACCOUNT_NAME}
        )

        if not availability_result.name_available:
            print(f"Storage name {STORAGE_ACCOUNT_NAME} is already in use. Try another name.")
            exit()

        # The name is available, so provision the account
        poller = storage_client.storage_accounts.begin_create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME,
                                                              {
                                                                  "location": LOCATION,
                                                                  "kind": "StorageV2",
                                                                  "sku": {"name": "Standard_LRS"}
                                                              }
                                                              )

        # Long-running operations return a poller object; calling poller.result()
        # waits for completion.
        account_result = poller.result()
        print(f"Provisioned storage account {account_result.name}")

        # Step 3: Retrieve the account's primary access key and generate a connection string.
        keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)

        print(f"Primary key for storage account: {keys.keys[0].value}")

        conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={keys.keys[0].value}"

        print(f"Connection string: {conn_string}")

        # Step 4: Provision the blob container in the account (this call is synchronous)
        CONTAINER_NAME = "blob-container-01"
        container = storage_client.blob_containers.create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, {})

        # The fourth argument is a required BlobContainer object, but because we don't need any
        # special values there, so we just pass empty JSON.

        print(f"Provisioned blob container {container.name}")
    except Exception as ex:
        raise ex
