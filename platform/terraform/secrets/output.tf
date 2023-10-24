# harbor OIDC secrets
output "registry_oidc_client_id" {
  value = module.secrets.network_id
  description = "Registry OIDC client ID"
}

output "registry_oidc_client_secret" {
  value = module.secrets.iam_cd_role
  description = "Registry OIDC client secret"
  sensitive = true
}

