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
  }
}

module "hosting-provider" {
  source          = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name    = local.name
}


