locals {
  oidc_issuer_url         = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name     = azurerm_resource_group.rg.name
  resource_group_location = azurerm_resource_group.rg.location
}

module "iac_pr_automation_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "atlantis"
  service_account_name    = "atlantis"
  role_definitions        = [
    { "name" = "Contributor", "scope" = "" },
    { "name" = "User Access Administrator", "scope" = "" },
    { "name" = "Key Vault Administrator", "scope" = "" }
  ]
  namespace = "atlantis"
  tags      = merge(local.tags, {
    "cg-devx.metadata.service" : "iac-pr-automation"
  })
}

module "ci_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "argo-workflow"
  service_account_name    = "argo-server"
  role_definitions        = [{ "name" = "Contributor", "scope" = "" }]
  namespace               = "argo"
  tags                    = merge(local.tags, {
    "cg-devx.metadata.service" : "continuous-integration"
  })
}

module "cert_manager_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "cert-manager"
  service_account_name    = "cert-manager"
  role_definitions        = [{ "name" = "Contributor", "scope" = "" }]
  namespace               = "cert-manager"
  tags                    = merge(local.tags, {
    "cg-devx.metadata.service" : "cert-manager"
  })
}

module "external_dns_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "external-dns"
  service_account_name    = "external-dns"
  role_definitions        = [{ "name" = "Contributor", "scope" = "" }]
  namespace               = "external-dns"
  tags                    = merge(local.tags, {
    "cg-devx.metadata.service" : "external-dns"
  })
}

module "secret_manager_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "vault"
  service_account_name    = "vault"
  role_definitions        = [{ "name" = "Key Vault Administrator", "scope" = "" }]
  namespace               = "vault"
  tags                    = merge(local.tags, {
    "cg-devx.metadata.service" : "secret-manager"
  })
}

# Cluster Autoscaler
module "cluster_autoscaler_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "cluster-autoscaler"
  service_account_name    = "cluster-autoscaler"
  role_definitions        = [{ "name" = "Contributor", "scope" = "" }]
  namespace               = "cluster-autoscaler"
  tags                    = merge(local.tags, {
    "cg-devx.metadata.service" : "cluster-autoscaler"
  })
}

# Cluster Backups Manager
module "backups_manager_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url         = local.oidc_issuer_url
  resource_group_name     = local.resource_group_name
  resource_group_location = local.resource_group_location
  name                    = "velero"
  service_account_name    = "velero"
  role_definitions        = [
    {
      "name"  = "Storage Blob Data Contributor",
      "scope" = "/resourceGroups/${local.resource_group_name}/providers/Microsoft.Storage/storageAccounts/${azurerm_storage_account.storage_account.name}"
    },
    {
      "name"  = "Contributor",
      "scope" = "/resourceGroups/${local.resource_group_name}"
    },
    {
      "name"  = "Contributor",
      "scope" = "/resourceGroups/${local.node_resource_group}"
    }
  ]
  namespace = "velero"
  tags      = merge(local.tags, {
    "cg-devx.metadata.service" : "backups-manager"
  })
  depends_on = [azurerm_storage_account.storage_account]
}