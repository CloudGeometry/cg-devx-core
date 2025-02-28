################################################################################
# network
################################################################################
output "network_id" {
  value       = module.hosting-provider.network_id
  description = "Platform primary K8s cluster network ID"
}

################################################################################
# IAM roles
################################################################################
output "iam_ci_role" {
  value       = module.hosting-provider.iam_ci_irsa_role
  description = "Continuous Integration IAM role for K8s service account"
}
output "iac_pr_automation_role" {
  value       = module.hosting-provider.iac_pr_automation_irsa_role
  description = "IaC PR automation IAM role for a K8s service account"
}
output "cert_manager_role" {
  value       = module.hosting-provider.cert_manager_irsa_role
  description = "Certificate Manager IAM role for a K8s service account"
}
output "external_dns_role" {
  value       = module.hosting-provider.external_dns_irsa_role
  description = "External DNS IAM role for a K8s service account"
}
output "secret_manager_role" {
  value       = module.hosting-provider.secret_manager_irsa_role
  description = "Secrets Manager IAM role for a K8s service account"
}
output "cluster_autoscaler_role" {
  value       = module.hosting-provider.cluster_autoscaler_irsa_role
  description = "Secrets Manager IAM role for a K8s service account"
}
output "backups_manager_role" {
  value       = module.hosting-provider.backups_manager_irsa_role
  description = "Cluster Backup Manager IAM role for a K8s service account"
}

################################################################################
# cluster
################################################################################
output "cluster_endpoint" {
  value       = module.hosting-provider.cluster_endpoint
  description = "K8s cluster admin API endpoint"
  sensitive   = true
}
output "cluster_certificate_authority_data" {
  value       = module.hosting-provider.cluster_certificate_authority_data
  description = "K8s cluster Certificate Authority certificate data"
  sensitive   = true
}
output "cluster_oidc_issuer_url" {
  value       = module.hosting-provider.cluster_oidc_issuer_url
  description = "The URL on the K8s cluster for the OpenID Connect identity provider"
  sensitive   = true
}
output "cluster_node_groups" {
  value       = module.hosting-provider.cluster_node_groups
  description = "K8s cluster node groups"
}

# Output part for Azure module only:
output "kube_config_raw" {
  value       = module.hosting-provider.kube_config_raw
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
  sensitive   = true
}

output "storage_account" {
  value       = module.hosting-provider.storage_account
  description = "The backups storage account name"
}

output "resource_group" {
  value       = module.hosting-provider.resource_group
  description = "Resource group name"
}

output "node_resource_group" {
  value       = module.hosting-provider.node_resource_group
  description = "Node resource group name"
}

# Cluster OIDC provider ARN for AWS only:
output "cluster_oidc_provider_arn" {
  value       = module.hosting-provider.cluster_oidc_provider_arn
  description = "Cluster OIDC provider"
  sensitive   = true
}
################################################################################
# secret manager
################################################################################
output "secret_manager_unseal_key" {
  value       = module.hosting-provider.secret_manager_unseal_key
  description = "Secret Manager seal key"
  sensitive   = true
}
output "secret_manager_unseal_key_ring" {
  value       = module.hosting-provider.secret_manager_unseal_key_ring
  description = "Secret Manager unseal key ring"
  sensitive   = true
}

################################################################################
# artifact storage
################################################################################
output "artifact_storage" {
  value       = module.hosting-provider.artifacts_storage
  description = "Continuous Integration Artifact Repository storage backend"
}

output "artifact_storage_endpoint" {
  value       = module.hosting-provider.artifacts_storage_endpoint
  description = "Continuous Integration Artifact Repository storage backend access endpoint"
}

output "artifacts_storage_access_key" {
  value       = module.hosting-provider.artifacts_storage_access_key
  sensitive   = true
  description = "Continuous Integration Artifact Repository storage account primary access key"
}

################################################################################
# backups storage
################################################################################
output "backups_storage" {
  value       = module.hosting-provider.backups_storage
  description = "Backups Manager storage backend"
}

