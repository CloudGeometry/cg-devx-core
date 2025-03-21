output "kube_config_raw" {
  value       = azurerm_kubernetes_cluster.aks_cluster.kube_admin_config_raw
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

################################################################################
# network
################################################################################
output "network_id" {
  value       = azurerm_virtual_network.vnet.id
  description = "Platform primary K8s cluster network ID"
}

################################################################################
# IAM roles
################################################################################
output "iam_ci_irsa_role" {
  value       = module.ci_sa.app_client_id
  description = "Continuous Integration IAM role for K8s service account"
}
output "iac_pr_automation_irsa_role" {
  value       = module.iac_pr_automation_sa.app_client_id
  description = "IaC PR automation IAM role for a K8s service account"
}
output "cert_manager_irsa_role" {
  value       = module.cert_manager_sa.app_client_id
  description = "Certificate Manager IAM role for a K8s service account"
}
output "external_dns_irsa_role" {
  value       = module.external_dns_sa.app_client_id
  description = "External DNS IAM role for a K8s service account"
}
output "secret_manager_irsa_role" {
  value       = module.secret_manager_sa.app_client_id
  description = "Secrets Manager IAM role for a K8s service account"
}

output "cluster_autoscaler_irsa_role" {
  description = "Cluster Autoscaler IAM Role ARN"
  value       = module.cluster_autoscaler_sa.app_client_id
}

output "backups_manager_irsa_role" {
  description = "Cluster Backup Manager IAM role for a K8s service account"
  value       = module.backups_manager_sa.app_client_id
}

################################################################################
# cluster
################################################################################
output "cluster_endpoint" {
  value       = azurerm_kubernetes_cluster.aks_cluster.kube_admin_config.0.host
  description = "K8s cluster admin API endpoint"
  sensitive   = true
}

output "cluster_certificate_authority_data" {
  value       = azurerm_kubernetes_cluster.aks_cluster.kube_admin_config.0.cluster_ca_certificate
  description = "K8s cluster Certificate Authority certificate data"
  sensitive   = true
}

output "cluster_oidc_issuer_url" {
  value       = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
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
  value       = azurerm_key_vault_key.secret_manager_unseal_kms_key.name
  description = "Secret Manager unseal key"
  sensitive   = true
}

output "secret_manager_unseal_key_ring" {
  value       = ""
  description = "Secret Manager unseal key ring"
  sensitive   = true
}

################################################################################
# artifact storage
################################################################################
output "artifacts_storage" {
  value       = azurerm_storage_container.artifacts_repository.name
  description = "Continuous Integration Artifact Repository storage backend"
}

output "artifacts_storage_endpoint" {
  value       = azurerm_storage_account.storage_account.primary_blob_endpoint
  description = "Continuous Integration Artifact Repository storage account primary endpoint"
}

output "artifacts_storage_access_key" {
  value       = azurerm_storage_account.storage_account.primary_access_key
  sensitive   = true
  description = "Continuous Integration Artifact Repository storage account primary access key"
}


# stub value for module compatibility
output "cluster_oidc_provider_arn" {
  value       = ""
  sensitive   = true
  description = "Cluster OIDC provider stub."
}

################################################################################
# backups storage
################################################################################
output "backups_storage" {
  description = "The backups storage container name"
  value       = azurerm_storage_container.backups_repository.name
}

output "storage_account" {
  description = "The backups storage account name"
  value       = azurerm_storage_account.storage_account.name
}

output "resource_group" {
  value       = azurerm_resource_group.rg.name
  description = "Resource group name"
}

output "node_resource_group" {
  value       = local.node_resource_group
  description = "Node resource group name"
}




