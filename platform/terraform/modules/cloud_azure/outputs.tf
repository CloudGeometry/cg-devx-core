output "kube_config_raw" {
  value       = azurerm_kubernetes_cluster.aks_cluster.kube_admin_config_raw
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

# network
output "network_id" {
  value = azurerm_virtual_network.vnet.id
  description = "Platform primary K8s cluster network ID"
}

# IAM roles
output "iam_cd_irsa_role" {
  value = module.cd_sa.app_client_id
  description = "Continuous Delivery IAM role for a K8s service account"
}
output "iam_ci_irsa_role" {
  value = module.ci_sa.app_client_id
  description = "Continuous Integration IAM role for K8s service account"
}
output "iac_pr_automation_irsa_role" {
  value = module.iac_pr_automation_sa.app_client_id
  description = "IaC PR automation IAM role for a K8s service account"
}
output "cert_manager_irsa_role" {
  value = module.cert_manager_sa.app_client_id
  description = "Certificate Manager IAM role for a K8s service account"
}
output "registry_irsa_role" {
  value = module.registry_sa.app_client_id
  description = "Registry IAM role for a K8s service account"
}
output "external_dns_irsa_role" {
  value = module.external_dns_sa.app_client_id
  description = "External DNS IAM role for a K8s service account"
}
output "secret_manager_irsa_role" {
  value = module.secret_manager_sa.app_client_id
  description = "Secrets Manager IAM role for a K8s service account"
}

# cluster
output "cluster_endpoint" {
  value = azurerm_kubernetes_cluster.aks_cluster.fqdn
  description = "K8s cluster admin API endpoint"
}
output "cluster_oidc_provider" {
  value = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  description = " K8s cluster OIDC provider endpoint"
}
output "cluster_certificate_authority_data" {
  value = azurerm_kubernetes_cluster.aks_cluster.kube_admin_config.0.cluster_ca_certificate
  description = "K8s cluster Certificate Authority certificate data"
  sensitive = true
}

# secret manager
output "secret_manager_unseal_key" {
  value = azurerm_key_vault.key_vault.id
  description = "Secret Manager seal key"
}

# artifact storage
output "artifacts_storage" {
  value = azurerm_storage_account.storage_account.id
  description = "Continuous Integration Artifact Repository storage backend"
}
