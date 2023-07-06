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
  source = "../modules/cloud-aws"

  # aws_account_id     = var.aws_account_id
  # cluster_name       = "cgdevx-demo"
  # node_capacity_type = "ON_DEMAND"
  # ami_type           = var.ami_type
  # instance_type      = var.instance_type
}

