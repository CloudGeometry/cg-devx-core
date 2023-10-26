terraform {
  # Remote backend configuration
  # <TF_HOSTING_REMOTE_BACKEND>
}

locals {
  cluster_name = "<PRIMARY_CLUSTER_NAME>"
  region       = "<CLOUD_REGION>"
  email        = ["<OWNER_EMAIL>"]
}

# Cloud Provider configuration
# <TF_HOSTING_PROVIDER>


module "hosting-provider" {
  source         = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name   = local.cluster_name
  region         = local.region
  alert_emails   = local.email
  ssh_public_key = var.ssh_public_key
}
