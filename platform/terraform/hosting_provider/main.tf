terraform {
  backend "s3" {
    bucket  = "cloud-aws-m-state-storage-w1"
    key     = "terraform/aws/terraform.tfstate"
    encrypt = true
  }
}

locals {
  name          = "gxcnew12eks"
  ProvisionedBy = "cgdevx"
}

provider "aws" {
  #  region = var.aws_region
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
  source          = "../modules/cloud_aws"
  cluster_name    = local.name
  node_group_type = "EKS"
  node_groups = [
    {
      name           = "gr1"
      instance_types = ["t3.medium"]
      min_size       = 3
      max_size       = 5
      desired_size   = 3
      capacity_type  = "ON_DEMAND"

    },
    {
      name           = "gr2-spot"
      instance_types = ["t3.medium", "t3.small"]
      min_size       = 3
      max_size       = 5
      desired_size   = 3
      capacity_type  = "SPOT"
    }
  ]
}


