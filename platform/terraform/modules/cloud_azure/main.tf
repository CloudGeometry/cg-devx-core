terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

locals {
  subnet_names = {
    for subnet in var.subnets : subnet => "${var.vnet_name}-${subnet}"
  }
  azs                   = [for i in range(1, var.az_count + 1) : tostring(i)]
  default_node_group    = var.node_groups[0]
  additional_node_pools = try(slice(var.node_groups, 1, length(var.node_groups)), [])
}


data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = "${var.cluster_name}-rg"
  location = var.region
  tags     = var.tags
}

resource "random_pet" "key_vault_name" {}

module "log_analytics_workspace" {
  source = "./modules/log_analytics"

  name                = "${var.cluster_name}-law"
  region              = var.region
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.tags
}


module "network" {
  //  for_each = var.networks
  source = "./modules/virtual_network"

  resource_group_name = azurerm_resource_group.rg.name
  region              = var.region
  vnet_name           = var.vnet_name
  address_space       = [var.cluster_network_cidr]
  subnets             = var.subnets

  tags = var.tags

  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
}

module "aks_cluster" {
  source = "./modules/aks"

  name                    = var.cluster_name
  dns_prefix              = lower(var.cluster_name)
  region                  = var.region
  resource_group_name     = azurerm_resource_group.rg.name
  resource_group_id       = azurerm_resource_group.rg.id
  private_cluster_enabled = var.aks_private_cluster
  vnet_subnet_id          = module.network.subnet_ids[local.subnet_names["priv"]]
  cluster_version         = var.cluster_version

  default_node_pool_vm_size            = local.default_node_group.instance_type
  default_node_pool_availability_zones = local.azs
  default_node_pool_max_count          = local.default_node_group.max_size
  default_node_pool_min_count          = local.default_node_group.min_size
  default_node_pool_node_count         = local.default_node_group.desired_size
  default_node_pool_node_labels        = var.cluster_node_labels

  tags = var.tags

  network_dns_service_ip = var.network_dns_service_ip
  network_service_cidr   = var.network_service_cidr

  log_analytics_workspace_id = module.log_analytics_workspace.id

  tenant_id                 = data.azurerm_client_config.current.tenant_id
  admin_group_object_ids    = var.admin_group_object_ids
  ssh_public_key            = var.ssh_public_key
  workload_identity_enabled = var.workload_identity_enabled

}


resource "random_string" "random_suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
  numeric = false
}

module "storage_account" {
  source = "./modules/storage_account"

  name                = lower("${var.cluster_name}${random_string.random_suffix.result}sa")
  region              = var.region
  resource_group_name = azurerm_resource_group.rg.name
}


module "node_pool" {
  source   = "./modules/node_pool"
  for_each = { for pool in local.additional_node_pools : pool["name"] => pool }

  resource_group_name   = azurerm_resource_group.rg.name
  kubernetes_cluster_id = module.aks_cluster.id

  name                 = each.key
  vm_size              = try(each.value.instance_type, var.additional_node_pool_vm_size)
  availability_zones   = local.azs
  vnet_subnet_id       = module.network.subnet_ids[local.subnet_names["priv"]]
  orchestrator_version = var.cluster_version
  enable_auto_scaling  = try(each.value.enable_auto_scaling, var.additional_node_pool_enable_auto_scaling)
  node_labels          = var.cluster_node_labels

  max_count  = try(each.value.max_size, var.additional_node_pool_max_count)
  min_count  = try(each.value.min_size, var.additional_node_pool_min_count)
  node_count = try(each.value.desired_size, var.additional_node_pool_node_count)


  tags = var.tags

  depends_on = [module.aks_cluster]
}

module "key_vault" {
  source = "./modules/key_vault"
  name   = "${var.cluster_name}-kv"

  region              = var.region
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = var.tags

  enabled_for_deployment          = var.key_vault_enabled_for_deployment
  enabled_for_disk_encryption     = var.key_vault_enabled_for_disk_encryption
  enabled_for_template_deployment = var.key_vault_enabled_for_template_deployment
  enable_rbac_authorization       = var.key_vault_enable_rbac_authorization
  purge_protection_enabled        = var.key_vault_purge_protection_enabled

  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
}

module "private_dns_zones" {
  for_each = var.private_dns_zones
  source   = "./modules/private_dns_zone"

  name                = each.value
  resource_group_name = azurerm_resource_group.rg.name
  virtual_networks_to_link = {
    (var.vnet_name) = {
      subscription_id     = data.azurerm_client_config.current.subscription_id
      resource_group_name = azurerm_resource_group.rg.name
    }
  }
}



module "key_vault_private_endpoint" {
  source = "./modules/private_endpoint"

  name                           = "${title(module.key_vault.name)}PrivateEndpoint"
  region                         = var.region
  resource_group_name            = azurerm_resource_group.rg.name
  subnet_id                      = module.network.subnet_ids[local.subnet_names["priv"]]
  tags                           = var.tags
  private_connection_resource_id = module.key_vault.id
  subresource_name               = "vault"
  private_dns_zone_group_name    = "KeyVaultPrivateDnsZoneGroup"
  private_dns_zone_group_ids     = [module.private_dns_zones["KeyVaultPrivate"].id]
}

module "blob_private_endpoint" {
  source = "./modules/private_endpoint"

  name                           = "${title(module.storage_account.name)}PrivateEndpoint"
  region                         = var.region
  resource_group_name            = azurerm_resource_group.rg.name
  subnet_id                      = module.network.subnet_ids[local.subnet_names["priv"]]
  tags                           = var.tags
  private_connection_resource_id = module.storage_account.id
  subresource_name               = "blob"
  private_dns_zone_group_name    = "BlobPrivateDnsZoneGroup"
  private_dns_zone_group_ids     = [module.private_dns_zones["BlobPrivate"].id]
}


module "aks_rbac" {
  source   = "./modules/aks_rbac"
  for_each = var.service_accounts

  oidc_issuer_url      = module.aks_cluster.oidc_issuer_url
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = each.value.name
  service_account_name = each.value.service_account_name
  role_definitions     = each.value.role_definitions
  namespace            = each.value.namespace

  depends_on = [module.aks_cluster]
}

