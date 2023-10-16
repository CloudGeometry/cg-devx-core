terraform {
  # Remote backend configuration
  # <TF_HOSTING_REMOTE_BACKEND>
}

locals {
  cluster_name  = "<PRIMARY_CLUSTER_NAME>"
  provisioned_by = "cgdevx"
  region        = "<CLOUD_REGION>"
  email         = ["<OWNER_EMAIL>"]
}

# Cloud Provider configuration
# <TF_HOSTING_PROVIDER>

## Azure provider configuration: 
# provider "azurerm" {
#   features {}
# }

module "hosting-provider" {
  source       = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name = local.cluster_name
  region       = local.region
  alert_emails = local.email
}
