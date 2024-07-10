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
  ## Example of node groups for the AWS cloud hosting provider
  ## Please note that for the  GPU or metal nodes, you need to check node type availability
  ## in your region and send service quota-increasing request to the support
  # node_groups            = [
  #   {
  #     name           = "default"
  #     instance_types = ["m5.large"]
  #     capacity_type  = "on_demand"
  #     min_size       = 3
  #     max_size       = 6
  #     disk_size      = 100
  #     desired_size   = 4
  #   },
  #   # {
  #   #   name           = "ml-node-group"
  #   #   instance_types = ["g5.xlarge"]
  #   #   gpu_enabled    = true
  #   #   capacity_type  = "on_demand"
  #   #   min_size       = 0
  #   #   max_size       = 1
  #   #   desired_size   = 1
  #   # },
  #   # {
  #   #   name           = "metal-node-group"
  #   #   instance_types = ["c5.metal"]
  #   #   gpu_enabled    = false
  #   #   capacity_type  = "on_demand"
  #   #   min_size       = 0
  #   #   max_size       = 1
  #   #   desired_size   = 1
  #   # },
  # ]
}
