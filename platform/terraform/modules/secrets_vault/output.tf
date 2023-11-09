# harbor OIDC secrets
output "registry_oidc_client_id" {
  value       = module.harbor.vault_oidc_client_id
  description = "Registry OIDC client ID"
}

output "registry_oidc_client_secret" {
  value       = module.harbor.vault_oidc_client_secret
  description = "Registry OIDC client secret"
  sensitive   = true
}

# harbor admin password
output "registry_admin_password" {
  value       = random_password.harbor_password.result
  description = "admin password"
  sensitive   = true
}

# harbor main robot password
output "registry_main_robot_password" {
  value       = random_password.harbor_main_robot_password.result
  description = "main-robot password"
  sensitive   = true
}

# code quality secrets
output "code_quality_oidc_client_id" {
  value       = module.sonarqube.vault_oidc_client_id
  description = "code quality OIDC client ID"
}

output "code_quality_oidc_client_secret" {
  value       = module.sonarqube.vault_oidc_client_secret
  description = "code quality OIDC client secret"
  sensitive   = true
}

output "code_quality_admin_password" {
  value       = random_password.sonarqube_password.result
  description = "code quality password"
  sensitive   = true
}