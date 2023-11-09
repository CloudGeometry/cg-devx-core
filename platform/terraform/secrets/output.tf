# harbor OIDC secrets
output "registry_oidc_client_id" {
  value       = module.secrets.registry_oidc_client_id
  description = "Registry OIDC client ID"
}

output "registry_oidc_client_secret" {
  value       = module.secrets.registry_oidc_client_secret
  description = "Registry OIDC client secret"
  sensitive   = true
}

# harbor admin password
output "registry_admin_user_password" {
  value       = module.secrets.registry_admin_password
  description = "admin password"
  sensitive   = true
}

# harbor main robot password
output "registry_main_robot_user_password" {
  value       = module.secrets.registry_main_robot_password
  description = "main-robot password"
  sensitive   = true
}

# code quality secrets
output "code_quality_oidc_client_id" {
  value       = module.secrets.code_quality_oidc_client_id
  description = "Registry OIDC client ID"
}

output "code_quality_oidc_client_secret" {
  value       = module.secrets.code_quality_oidc_client_secret
  description = "Registry OIDC client secret"
  sensitive   = true
}

output "code_quality_admin_user_password" {
  value       = module.secrets.code_quality_admin_password
  description = "admin password"
  sensitive   = true
}
