resource "google_kms_key_ring" "vault_key_ring" {
  name     = "${local.name}-vault-${random_string.uniq_kms_suffix.result}"
  location = "global"
  project  = local.project_id
}

resource "google_kms_crypto_key" "vault_unseal_key" {
  name            = "vault-unseal"
  key_ring        = google_kms_key_ring.vault_key_ring.id
  # 365 days
  rotation_period = "31536000s"

  lifecycle {
    prevent_destroy = false
  }
}

variable "secret_manager_unseal_crypto_key_name" {
  description = "Name of the key to be used"
  type        = string
  default     = "vault-unseal"
}

resource "random_string" "uniq_kms_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}
