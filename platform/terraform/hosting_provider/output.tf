# network
output "network_id" {
  value = module.hosting-provider.network_id
  description = "Platform primary K8s cluster network ID"
}

# IAM roles
output "iam_cd_role" {
  value = module.hosting-provider.iam_cd_role
  description = "Continuous Delivery IAM role for a K8s service account"
}
output "iam_ci_role" {
  value = module.hosting-provider.iam_ci_role
  description = "Continuous Integration IAM role for K8s service account"
}
output "iac_pr_automation_role" {
  value = module.hosting-provider.iac_pr_automation_irsa_role
  description = "IaC PR automation IAM role for a K8s service account"
}
output "cert_manager_role" {
  value = module.hosting-provider.cert_manager_irsa_role
  description = "Certificate Manager IAM role for a K8s service account"
}
output "registry_role" {
  value = module.hosting-provider.registry_irsa_role
  description = "Registry IAM role for a K8s service account"
}
output "external_dns_role" {
  value = module.hosting-provider.external_dns_irsa_role
  description = "External DNS IAM role for a K8s service account"
}
output "secret_manager_role" {
  value = module.hosting-provider.secret_manager_irsa_role
  description = "Secrets Manager IAM role for a K8s service account"
}

# cluster
output "cluster_endpoint" {
  value = module.hosting-provider.cluster_endpoint
  description = "K8s cluster admin API endpoint"
}
output "cluster_oidc_provider" {
  value = module.hosting-provider.oidc_provider
  description = " K8s cluster OIDC provider endpoint"
}
output "cluster_certificate_authority_data" {
  value = module.hosting-provider.cluster_certificate_authority_data
  description = "K8s cluster Certificate Authority certificate data"
}

# secret manager
output "secret_manager_seal_key" {
  value = module.hosting-provider.secret_manager_unseal_kms_key
  description = "Secret Manager seal key"
}

# artifact storage
output "artifact_storage" {
  value = module.hosting-provider.artifacts_storage
  description = "Continuous Integration Artifact Repository storage backend"
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
