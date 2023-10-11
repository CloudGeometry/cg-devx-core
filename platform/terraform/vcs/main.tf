terraform {
  backend "s3" {
    bucket = ""
    key    = "terraform/github/terraform.tfstate"

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

module "vcs" {
  source = "../modules/vcs-github"

}

