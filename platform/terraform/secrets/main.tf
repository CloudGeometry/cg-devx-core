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

locals {
  cluster_name   = "<PRIMARY_CLUSTER_NAME>"
  provisioned_by = "cgdevx"
}

module "secrets" {
  source = "../modules/secrets_vault"

  cluster_name                            = local.cluster_name
  workloads                               = var.workloads
  vcs_bot_ssh_public_key                  = var.vcs_bot_ssh_public_key
  vcs_bot_ssh_private_key                 = var.vcs_bot_ssh_private_key
  vcs_token                               = var.vcs_token
  atlantis_repo_webhook_secret            = var.atlantis_repo_webhook_secret
  atlantis_repo_webhook_url               = var.atlantis_repo_webhook_url
  cd_webhook_secret                       = var.cd_webhook_secret
  vault_token                             = var.vault_token
  cluster_endpoint                        = var.cluster_endpoint
  cluster_ssh_public_key                  = var.cluster_ssh_public_key
  tf_backend_storage_access_key           = var.tf_backend_storage_access_key
  cloud_binary_artifacts_store_access_key = var.cloud_binary_artifacts_store_access_key
  image_registry_auth                     = var.image_registry_auth
}
