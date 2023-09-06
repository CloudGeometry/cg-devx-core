terraform {

#Placeholder for remote backend configuration
}

locals {
  name            = "<PRIMARY_CLUSTER_NAME>"
  ProvisionedBy   = "cgdevx"
}

# configure cloud provider through env variables
# AWS_REGION and AWS_PROFILE for local run and through assuming IAM role in CI runner
# so, for local run required:
# export AWS_REGION="<CLOUD_REGION>"
# export AWS_PROFILE="<CLOUD_PROFILE>"
provider "aws" {
  default_tags {
    tags = {
      ClusterName   = local.name
      ProvisionedBy = local.ProvisionedBy
    }
  ]
  cluster_node_labels = {
    "Provisioned-By" = "Terraform"
  }
  tags = {
    createdWith   = "Terraform"
    ProvisionedBy = "local"
  }
}

module "hosting-provider" {
  source          = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name    = local.name
}



output "fqdn" {
  value       = module.hosting-provider-azure.fqdn
  description = "FQDN of the Azure Kubernetes Managed Cluster"
}

output "apps" {
  value       = module.hosting-provider-azure.apps
  description = "Name and ID for all AKS Rbac apps"
}
