# network
################################################################################
output "network_id" {
  value       = module.vpc.network_id
  description = "Platform primary K8s cluster network ID"
}

################################################################################
# IAM roles
################################################################################
output "iam_ci_irsa_role" {
  value       = module.ci_sa.service_account_email
  description = "Continuous Integration IAM role for K8s service account"
}
output "iac_pr_automation_irsa_role" {
  value       = module.iac_pr_automation_sa.service_account_email
  description = "IaC PR automation service account for a K8s service account"
}
output "cert_manager_irsa_role" {
  value       = module.cert_manager_sa.service_account_email
  description = "Certificate Manager IAM role for a K8s service account"
}
output "external_dns_irsa_role" {
  value       = module.external_dns_sa.service_account_email
  description = "External DNS IAM role for a K8s service account"
}
output "secret_manager_irsa_role" {
  value       = module.secret_manager_sa.service_account_email
  description = "Secrets Manager IAM role for a K8s service account"
}

output "cluster_autoscaler_irsa_role" {
  value       = ""
  description = "Cluster Autoscaler IAM Role ARN"
}

output "backups_manager_irsa_role" {
  description = "Cluster Backup Manager IAM role for a K8s service account"
  value       = module.backups_manager_sa.service_account_email
}

################################################################################
# cluster
################################################################################
output "cluster_endpoint" {
  value       = "https://${module.gke.endpoint}"
  description = "K8s cluster admin API endpoint"
  sensitive   = true
}

output "cluster_certificate_authority_data" {
  value       = module.gke.ca_certificate
  description = "K8s cluster Certificate Authority certificate data"
  sensitive   = true
}

output "cluster_oidc_issuer_url" {
  value       = module.gke.master_version
  description = "Cluster OIDC provider"
  sensitive   = true
}

output "cluster_node_groups" {
  value       = var.node_groups
  description = "Cluster node groups"
}

################################################################################
# secret manager
################################################################################
output "secret_manager_unseal_key" {
  value       = var.secret_manager_unseal_crypto_key_name
  description = "Secret Manager seal key"
  sensitive   = true
}

output "secret_manager_unseal_key_ring" {
  value       = google_kms_key_ring.vault_key_ring.name
  description = "Secret Manager unseal key ring"
  sensitive   = true
}

################################################################################
# artifact storage
################################################################################
output "artifacts_storage" {
  value       = google_storage_bucket.artifacts_repository.id
  description = "Continuous Integration Artifact Repository storage backend"
}

output "artifacts_storage_endpoint" {
  value       = google_storage_bucket.artifacts_repository.url
  description = "Continuous Integration Artifact Repository storage account primary endpoint"
}
################################################################################
# backups storage
################################################################################
output "backups_storage" {
  description = "The backups storage S3 bucket name"
  value       = google_storage_bucket.backups_repository.id
}

# stub value for module compatibility
output "artifacts_storage_access_key" {
  value       = ""
  sensitive   = true
  description = "Continuous Integration Artifact Repository storage account primary access key"
}


# stub value for module compatibility
output "cluster_oidc_provider_arn" {
  value       = ""
  sensitive   = true
  description = "Cluster OIDC provider stub."
}

# stub value for module compatibility
output "kube_config_raw" {
  value       = ""
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

# stub value for module compatibility
output "storage_account" {
  value       = ""
  description = "The backups storage account name"
}

# stub value for module compatibility
output "resource_group" {
  value       = ""
  description = "Resource group name"
}

# stub value for module compatibility
output "node_resource_group" {
  value       = ""
  description = "Node resource group name"
}
