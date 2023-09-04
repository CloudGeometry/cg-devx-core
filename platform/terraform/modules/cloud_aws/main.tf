locals {
  region          = ""
  tags            = ""
}

provider "aws" {
  region = local.region
}

provider "kubernetes" {
}
