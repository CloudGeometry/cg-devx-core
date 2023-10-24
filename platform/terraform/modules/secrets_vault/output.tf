# harbor OIDC secrets
output "registry_oidc_client_id" {
  value = module.harbor.vault_oidc_client_id
  description = "Registry OIDC client ID"
}

output "registry_oidc_client_secret" {
  value = module.harbor.vault_oidc_client_secret
  description = "Registry OIDC client secret"
  sensitive = true
}

# harbor main robot password
output "registry_main_robot_password" {
  value = random_password.harbor_main_robot_password.result
  description = "main-robot password"
  sensitive = true
}

