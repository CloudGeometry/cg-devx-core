terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.75"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

data "azurerm_client_config" "current" {}

locals {
  subnets                      = ["public", "private", "internal"]
  vnet_name                    = "${var.cluster_name}-vnet"
  log_analytics_retention_days = 30
  subnet_names                 = {
    for subnet in local.subnets : subnet => "${local.vnet_name}-${subnet}"
  }
  tags = {
    cgx_name = var.cluster_name
  }
  azs                   = [for i in range(1, var.az_count + 1) : tostring(i)]
  default_node_group    = var.node_groups[0]
  additional_node_pools = try(slice(var.node_groups, 1, length(var.node_groups)), [])
  max_pods              = 250
  node_admin_username   = "azadmin"
}


resource "azurerm_resource_group" "rg" {
  name     = "${var.cluster_name}-rg"
  location = var.region
  tags     = local.tags
}

# log analytics
resource "azurerm_log_analytics_workspace" "log_analytics_workspace" {
  name                = "${var.cluster_name}-law"
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.tags
  retention_in_days   = local.log_analytics_retention_days

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_log_analytics_solution" "container_insights_solution" {
  solution_name         = "ContainerInsights"
  location              = var.region
  resource_group_name   = azurerm_resource_group.rg.name
  workspace_resource_id = azurerm_log_analytics_workspace.log_analytics_workspace.id
  workspace_name        = azurerm_log_analytics_workspace.log_analytics_workspace.name

  plan {
    product   = "OMSGallery/ContainerInsights"
    publisher = "Microsoft"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
# ---

# network
resource "azurerm_virtual_network" "vnet" {
  name                = local.vnet_name
  address_space       = [var.cluster_network_cidr]
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_subnet" "subnets" {
  count = length(local.subnets)

  name                                          = "${local.vnet_name}-${local.subnets[count.index]}"
  resource_group_name                           = azurerm_resource_group.rg.name
  virtual_network_name                          = azurerm_virtual_network.vnet.name
  address_prefixes                              = [cidrsubnet(var.cluster_network_cidr, 4, count.index)]
  private_endpoint_network_policies_enabled     = true
  private_link_service_network_policies_enabled = false

}
# ---

# aks
resource "azurerm_user_assigned_identity" "aks_identity" {
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.region
  tags                = local.tags

  name = "${var.cluster_name}Identity"

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                             = var.cluster_name
  location                         = var.region
  resource_group_name              = azurerm_resource_group.rg.name
  kubernetes_version               = var.cluster_version
  dns_prefix                       = lower(var.cluster_name)
  private_cluster_enabled          = false
  workload_identity_enabled        = true
  oidc_issuer_enabled              = true
  open_service_mesh_enabled        = false
  image_cleaner_enabled            = false
  azure_policy_enabled             = true
  http_application_routing_enabled = false

  default_node_pool {
    name                   = local.default_node_group.name
    vm_size                = local.default_node_group.instance_types[0]
    vnet_subnet_id         = azurerm_subnet.subnets[index(keys(local.subnet_names), "private")].id
    # pod_subnet_id          = [] ?? do we need it
    zones                  = local.azs
    node_labels            = var.cluster_node_labels
    enable_auto_scaling    = true
    enable_host_encryption = false
    enable_node_public_ip  = false
    max_pods               = local.max_pods
    max_count              = local.default_node_group.max_size
    min_count              = local.default_node_group.min_size
    node_count             = local.default_node_group.desired_size
    tags                   = local.tags
  }

  linux_profile {
    admin_username = local.node_admin_username
    ssh_key {
      key_data = var.ssh_public_key
    }
  }

  identity {
    type         = "UserAssigned"
    identity_ids = tolist([azurerm_user_assigned_identity.aks_identity.id])
  }
  # TODO: update
  network_profile {
    # all defaults here
    dns_service_ip    = "10.2.0.10"
    network_plugin    = "azure"
    outbound_type     = "loadBalancer"
    service_cidr      = "10.2.0.0/24"
    load_balancer_sku = "standard"
  }

  oms_agent {
    msi_auth_for_monitoring_enabled = true
    log_analytics_workspace_id      = azurerm_log_analytics_workspace.log_analytics_workspace.id
  }

  azure_active_directory_role_based_access_control {
    managed            = true
    tenant_id          = data.azurerm_client_config.current.tenant_id
    azure_rbac_enabled = true
  }


  lifecycle {
    ignore_changes = [
      kubernetes_version,
      tags
    ]
  }
}
# ---

resource "random_string" "random_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}

resource "azurerm_storage_account" "storage_account" {
  name                = lower("${replace(replace(var.cluster_name, "_", ""), "-", "")}ar${random_string.random_suffix.result}")
  resource_group_name = azurerm_resource_group.rg.name

  location                      = var.region
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  tags                          = local.tags
  public_network_access_enabled = false

  network_rules {
    default_action = "Allow"
  }

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

# todo: create blob storage

resource "azurerm_kubernetes_cluster_node_pool" "node_pool" {
  for_each = {for pool in local.additional_node_pools : pool["name"] => pool}

  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id

  name                  = each.key
  vm_size               = each.value.instance_types
  zones                 = local.azs
  vnet_subnet_id        = azurerm_subnet.subnets[index(keys(local.subnet_names), "private")].id
  max_count             = each.value.max_size
  min_count             = each.value.min_size
  node_count            = each.value.desired_size
  node_labels           = var.cluster_node_labels
  orchestrator_version  = var.cluster_version
  tags                  = local.tags
  # check with serg
  enable_node_public_ip = false
  max_pods              = local.max_pods
  priority              = each.value.capacity_type

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

resource "azurerm_key_vault" "key_vault" {
  name = "${var.cluster_name}-kv"

  location            = var.region
  sku_name            = "standard"
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = local.tags

  enabled_for_deployment          = false
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = false
  enable_rbac_authorization       = true
  purge_protection_enabled        = true
  public_network_access_enabled   = false

  soft_delete_retention_days = 7

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

# todo: create key

# dns zones
resource "azurerm_private_dns_zone" "key_vault_private" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
resource "azurerm_private_dns_zone" "blob_storage_private" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "key_vault_private_link" {
  name                  = "link_to_${lower(basename(local.vnet_name))}"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.key_vault_private.name
  virtual_network_id    = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.Network/virtualNetworks/${local.vnet_name}"

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
resource "azurerm_private_dns_zone_virtual_network_link" "blob_storage_private_link" {
  name                  = "link_to_${lower(basename(local.vnet_name))}"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.blob_storage_private.name
  virtual_network_id    = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.Network/virtualNetworks/${local.vnet_name}"

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
# ---

# private endpoints
resource "azurerm_private_endpoint" "key_vault_private_endpoint" {
  name                = "${title(azurerm_key_vault.key_vault.name)}PrivateEndpoint"
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnets[index(keys(local.subnet_names), "private")].id
  tags                = local.tags

  private_service_connection {
    name                           = "${title(azurerm_key_vault.key_vault.name)}PrivateEndpointConnection"
    private_connection_resource_id = azurerm_key_vault.key_vault.id
    is_manual_connection           = false
    subresource_names              = ["vault"]
  }

  private_dns_zone_group {
    name                 = "KeyVaultPrivateDnsZoneGroup"
    private_dns_zone_ids = [azurerm_private_dns_zone.key_vault_private.id]
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_private_endpoint" "blob_private_endpoint" {
  name                = "${title(azurerm_storage_account.storage_account.name)}PrivateEndpoint"
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnets[index(keys(local.subnet_names), "private")].id
  tags                = local.tags

  private_service_connection {
    name                           = "${title(azurerm_storage_account.storage_account.name)}PrivateEndpointConnection"
    private_connection_resource_id = azurerm_storage_account.storage_account.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }

  private_dns_zone_group {
    name                 = "BlobPrivateDnsZoneGroup"
    private_dns_zone_ids = [azurerm_private_dns_zone.blob_storage_private.id]
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
# ---

# service accounts
module "iac_pr_automation_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "atlantis"
  service_account_name = "atlantis"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "atlantis"

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

module "cd_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "argocd"
  service_account_name = "argocd-server"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "argocd"

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

module "registry_sa" {
  source = "./modules/aks_rbac"

  oidc_issuer_url      = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "harbor"
  service_account_name = "default"
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "harbor"

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
  role_definitions     = [{ "name" = "Contributor", "scope" = "" }]
  namespace            = "vault"

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}
# ---
