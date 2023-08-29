output "kube_config_raw" {
  value       = module.aks_cluster.kube_config_raw
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

output "private_fqdn" {
  value       = module.aks_cluster.private_fqdn
  sensitive   = true
  description = "The FQDN for the Kubernetes Cluster."
}

output "public_ip_address" {
  description = "Specifies the private IP address of the firewall."
  value       = module.firewall.public_ip_address
}