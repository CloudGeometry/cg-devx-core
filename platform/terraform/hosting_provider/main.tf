terraform {
  # Remote backend configuration
  # <TF_HOSTING_REMOTE_BACKEND>
}

locals {
  name          = "<PRIMARY_CLUSTER_NAME>"
  ProvisionedBy = "cgdevx"
  region        = "<CLOUD_REGION>"
  email         = ["<OWNER_EMAIL>"]
}

# Provider configuration
# <TF_HOSTING_PROVIDER>

module "hosting-provider" {
  source       = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name = local.name
  region       = local.region
  alert_emails = local.email
}


