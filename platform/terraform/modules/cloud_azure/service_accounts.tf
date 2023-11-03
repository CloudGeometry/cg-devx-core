module "iac_pr_automation_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "atlantis"
  service_account_name = "atlantis"
  role_definitions     = [
    { "name" = "Contributor", "scope" = "" },
    { "name" = "Key Vault Administrator", "scope" = "" }
  ]
  namespace = "atlantis"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

module "ci_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "argo-workflow"
  service_account_name = "argo-server"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "argo"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

module "cert_manager_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "cert-manager"
  service_account_name = "cert-manager"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "cert-manager"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

module "external_dns_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "external-dns"
  service_account_name = "external-dns"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "external-dns"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

module "secret_manager_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "vault"
  service_account_name = "vault"
  role_definitions     = [{ "name" = "Key Vault Administrator", "scope" = "" }]
  namespace            = "vault"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}