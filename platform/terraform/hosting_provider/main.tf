terraform {

#Placeholder for remote backend configuration
}

locals {
  name            = "<PRIMARY_CLUSTER_NAME>"
  ProvisionedBy   = "cgdevx"
}

# configure cloud provider through env variables
# AWS_REGION and AWS_PROFILE for local run and through assuming IAM role in CI runner
# so, for loval run required:
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
provider "kubernetes" {
  host                   = module.hosting-provider.cluster_endpoint
  cluster_ca_certificate = base64decode(module.hosting-provider.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", module.hosting-provider.cluster_name]
  }
}
module "hosting-provider" {
  source          = "../modules/cloud_<CLOUD_PROVIDER>"
  cluster_name    = local.name
}


