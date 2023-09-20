terraform {
 
  # backend "s3" {
  #   bucket = "<STATE_STORE_BUCKET>"
  #   key    = "terraform/vault/terraform.tfstate"

  #   region  = "<CLOUD_REGION>"
  #   encrypt = true
  # }
  required_providers {
    vault = {
      source = "hashicorp/vault"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
  }
}

# Configure Vault & Cloud Providers
provider "vault" {
  skip_tls_verify = "true"
}

provider "aws" {
  region = "<CLOUD_REGION>"
}

locals {
  cluster_name = "<PRIMARY_CLUSTER_NAME>"
}

module "secrets" {
  source = "../modules/secrets_vault"

  cluster_name                 = local.cluster_name
  demo_workload_enabled        = var.demo_workload_enabled
  cgdevxbot_ssh_public_key     = var.vcs_bot_ssh_public_key
  cgdevxbot_ssh_private_key    = var.vcs_bot_ssh_private_key
  b64_docker_auth              = var.b64_docker_auth
  <GIT_PROVIDER>_token         = var.<GIT_PROVIDER>_token
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  atlantis_repo_webhook_url    = var.atlantis_repo_webhook_url
  vault_token                  = var.vault_token
}
