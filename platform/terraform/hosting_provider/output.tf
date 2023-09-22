# network
output "network_id" {
  value = module.hosting-provider.network_id
}

# IAM roles
output "iam_cd_role" {
  value = module.hosting-provider.iam_cd_role
}
output "iam_ci_role" {
  value = module.hosting-provider.iam_ci_role
}
output "iac_pr_automation_role" {
  value = module.hosting-provider.iac_pr_automation_irsa_role
}
output "cert_manager_role" {
  value = module.hosting-provider.cert_manager_irsa_role
}
output "registry_role" {
  value = module.hosting-provider.registry_irsa_role
}
output "external_dns_role" {
  value = module.hosting-provider.external_dns_irsa_role
}
output "secret_manager_role" {
  value = module.hosting-provider.secret_manager_irsa_role
}

# cluster
output "cluster_endpoint" {
  value = module.hosting-provider.cluster_endpoint
}
output "cluster_oidc_provider" {
  value = module.hosting-provider.oidc_provider
}
output "cluster_certificate_authority_data" {
  value = module.hosting-provider.cluster_certificate_authority_data
}

# secret manager
output "secret_manager_seal_key" {
  value = module.hosting-provider.secret_manager_unseal_kms_key
}


###########
# Output part for Azure module only:
# output "kube_config_raw" {
#   value       = module.hosting-provider.kube_config_raw
#   sensitive   = true
#   description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
# }

# output "fqdn" {
#   value       = module.hosting-provider.fqdn
#   description = "FQDN of the Azure Kubernetes Managed Cluster"
# }

# output "apps" {
#   value       = module.hosting-provider.apps
#   description = "Name and ID for all AKS Rbac apps"
# }
