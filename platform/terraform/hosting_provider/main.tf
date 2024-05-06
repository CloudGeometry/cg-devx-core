terraform {
  # Remote backend configuration
  # <TF_HOSTING_REMOTE_BACKEND>
}

locals {
  cluster_name = "<PRIMARY_CLUSTER_NAME>"
  region       = "<CLOUD_REGION>"
  email        = ["<OWNER_EMAIL>"]
  domain_name  = "<DOMAIN_NAME>"
  tags = {
    "cg-devx.cost-allocation.cost-center" = "platform"
    "cg-devx.metadata.cluster-name"       = local.cluster_name
    "cg-devx.metadata.owner"              = "${local.cluster_name}-admin"
    "provisioned-by"                      = "cg-devx"
  }
  labels = {
    "cg-devx.cost-allocation.cost-center" = "platform"
    "cg-devx.metadata.cluster-name"       = local.cluster_name
    "cg-devx.metadata.owner"              = "${local.cluster_name}-admin"
    "provisioned-by"                      = "cg-devx"
  }
}

# Cloud Provider configuration
# <TF_HOSTING_PROVIDER>


module "hosting-provider" {
  source                 = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name           = local.cluster_name
  region                 = local.region
  alert_emails           = local.email
  cluster_ssh_public_key = var.cluster_ssh_public_key
  tags                   = local.tags
  cluster_node_labels    = local.labels
  domain_name            = local.domain_name
  workloads              = var.workloads
}
