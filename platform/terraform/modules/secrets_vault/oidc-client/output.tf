output "vault_oidc_client_id" {
  value = vault_identity_oidc_client.app.client_id
}

output "vault_oidc_app_name" {
  value = vault_identity_oidc_client.app.name
}