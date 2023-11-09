terraform {

  required_providers {
    vault = {
      source = "hashicorp/vault"
    }
  }
}

resource "vault_identity_oidc_assignment" "app" {
  name      = var.app_name
  group_ids = var.identity_group_ids
}

resource "vault_identity_oidc_client" "app" {
  name          = var.app_name
  key           = var.oidc_provider_key_name
  redirect_uris = var.redirect_uris
  assignments   = [
    vault_identity_oidc_assignment.app.name,
  ]
  id_token_ttl     = 2400
  access_token_ttl = 7200
  client_type      = "confidential"
}

data "vault_identity_oidc_client_creds" "creds" {
  name = var.app_name

  depends_on = [
    vault_identity_oidc_client.app
  ]

}

resource "vault_generic_secret" "creds" {
  path = "${var.secret_mount_path}/oidc/${var.app_name}"

  depends_on = [
    vault_identity_oidc_client.app
  ]

  data_json = <<EOT
{
  "client_id" : "${data.vault_identity_oidc_client_creds.creds.client_id}",
  "client_secret" : "${data.vault_identity_oidc_client_creds.creds.client_secret}"
}
EOT
}
