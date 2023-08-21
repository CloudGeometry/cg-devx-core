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
  #

}
/*
provider "kubernetes" {
  host                   = module.cloud_aws.cluster_endpoint
  cluster_ca_certificate = base64decode(module.cloud_aws.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", module.cloud_aws.cluster_name]
  }
}



module "cloud_aws" {
  source       = "../modules/cloud_aws"
  cluster_name = "gxc"
  node_groups = [
    {
      name           = "gr1"
      instance_types = ["t3.small"]
      desired_size   = 3
      min_size       = 3
      max_size       = 5
      capacity_type  = "on-demand"

    },
    {
      name           = "gr2-spot"
      instance_types = ["t3.medium", "t3.small"]
      dmin_size      = 3
      max_size       = 5
      esired_size    = 3
      capacity_type  = "spot"
    }
  ]
}
*/
