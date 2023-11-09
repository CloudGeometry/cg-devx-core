terraform {
  # Remote backend configuration
  # <TF_SECRETS_REMOTE_BACKEND>

  required_providers {
    vault = {
      source = "hashicorp/vault"
    }
  }
}

# Vault configuration
provider "vault" {
  skip_tls_verify = "true"
}

# Cloud Provider configuration
# <TF_HOSTING_PROVIDER>

locals {
  cluster_name   = "<PRIMARY_CLUSTER_NAME>"
  provisioned_by = "cgdevx"
  ### Workload groups definition bellow
  workloads      = {
    # "workload-demo" = {
    # },
  }
}

module "secrets" {
  source = "../modules/secrets_vault"

  cluster_name                 = local.cluster_name
  workloads                    = local.workloads
  vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
  vcs_bot_ssh_private_key      = var.vcs_bot_ssh_private_key
  vcs_token                    = var.vcs_token
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  atlantis_repo_webhook_url    = var.atlantis_repo_webhook_url
  vault_token                  = var.vault_token
  cluster_endpoint             = var.cluster_endpoint
}
