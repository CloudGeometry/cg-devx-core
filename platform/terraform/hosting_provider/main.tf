terraform {
  backend "s3" {
    bucket = ""
    key    = "terraform/aws/terraform.tfstate"

    region  = ""
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      ClusterName   = "cgdevx-demo"
      ProvisionedBy = "cgdevx"
    }
  }
}

module "hosting-provider" {
  source       = "../modules/cloud-aws"
  cluster_name = "gxcabcdefghj"
  node_groups = [
    {
      name           = "gr1"
      instance_types = ["t3.small"]
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


