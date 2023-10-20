terraform {
  # Remote backend configuration
  # <TF_ARTIFACT_REGISTRY_REMOTE_BACKEND>
}

provider "harbor" {
}

locals {
### some harbor variables here
}

module "users" {
  source      = "../modules/artifact_registry_harbor"
#  users       = local.users
}