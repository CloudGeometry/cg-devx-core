# cloud_aws terraform module for cgdevx

Example Usage:

```
terraform {
}

locals {
  name          = "cgdevx-demo-cluster"
  ProvisionedBy = "cgdevx"
}

# configure cloud provider through env variables
# AWS_REGION and AWS_PROFILE for local run and through assuming IAM role in CI runner
# so, for loval run required:
# export AWS_REGION="<CLOUD_REGION>"
# export AWS_PROFILE="<CLOUD_PROFILE>"
#
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
#path to the module here
  source          = "../modules/cloud_aws"
  cluster_name    = local.name
  node_groups = [
    {
      name           = "gr1"
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      capacity_type  = "ON_DEMAND"

    },
    {
      name           = "gr2-spot"
      instance_types = ["t3.medium", "t3.small"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      capacity_type  = "SPOT"
    }
  ]
}
```