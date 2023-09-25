# network
output "network_id" {
  value = module.hosting-provider.network_id
}

# IAM roles
output "iam_argoworkflow_role" {
  value = module.hosting-provider.iam_argoworkflow_role
}
output "atlantis_role" {
  value = module.hosting-provider.atlantis_irsa_role
}
output "cert_manager_role" {
  value = module.hosting-provider.cert_manager_irsa_role
}
output "harbor_role" {
  value = module.hosting-provider.harbor_irsa_role
}
output "external_dns_role" {
  value = module.hosting-provider.external_dns_irsa_role
}
output "vault_role" {
  value = module.hosting-provider.vault_irsa_role
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