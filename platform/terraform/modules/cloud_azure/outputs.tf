output "kube_config_raw" {
  value       = module.aks_cluster.kube_config_raw
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

output "fqdn" {
  value       = module.aks_cluster.fqdn
  description = "The FQDN of the Azure Kubernetes Managed Cluster"
}
output "apps" {
  value = { for k, v in var.service_accounts : v.name => module.aks_rbac[k].app_client_id }
    description = "Name and ID for all AKS Rbac apps"
}