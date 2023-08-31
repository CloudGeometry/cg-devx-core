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
  # Some glue to ensure correct indices 
  subnet_lookup = {
    system   = index(var.networks["aks"].subnets.*.name, "SystemSubnet"),
    user     = index(var.networks["aks"].subnets.*.name, "UserSubnet"),
    pods     = index(var.networks["aks"].subnets.*.name, "PodSubnet"),
    vms      = index(var.networks["aks"].subnets.*.name, "DevXGeneralSubnet")
    firewall = index(var.networks["hub"].subnets.*.name, "AzureFirewallSubnet")
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = "${var.aks_cluster_name}-rg"
  location = var.region
  tags     = var.tags
}

resource "random_pet" "key_vault_name" {}

module "log_analytics_workspace" {
  source = "./modules/log_analytics"

  name                = "${var.aks_cluster_name}-law"
  region            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.tags
}


module "network" {
  for_each = var.networks
  source   = "./modules/virtual_network"

  resource_group_name = azurerm_resource_group.rg.name
  region            = var.region
  vnet_name           = each.value.vnet_name
  address_space       = each.value.address_space
  subnets             = each.value.subnets

  tags = var.tags

  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
}


module "vnet_peering" {
  source = "./modules/virtual_network_peering"

  vnet_1_name         = module.network["hub"].name
  vnet_1_id           = module.network["hub"].vnet_id
  vnet_1_rg           = azurerm_resource_group.rg.name
  vnet_2_name         = module.network["aks"].name
  vnet_2_id           = module.network["aks"].vnet_id
  vnet_2_rg           = azurerm_resource_group.rg.name
  peering_name_1_to_2 = "${module.network["hub"].name}To${module.network["aks"].name}"
  peering_name_2_to_1 = "${module.network["aks"].name}To${module.network["hub"].name}"
}

module "firewall" {
  source = "./modules/firewall"

  name                         = "${var.aks_cluster_name}-fw"
  resource_group_name          = azurerm_resource_group.rg.name
  region                     = var.region
  pip_name                     = "${var.firewall_name}PublicIp"
  subnet_id                    = module.network["hub"].subnet_ids[var.networks.hub.subnets[local.subnet_lookup["firewall"]].name]
  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
}

module "routetable" {
  source = "./modules/route_table"

  resource_group_name = azurerm_resource_group.rg.name
  region            = var.region
  route_table_name    = var.route_table_name
  route_name          = var.route_name
  firewall_private_ip = module.firewall.private_ip_address
  subnets_to_associate = {
    (var.networks.aks.subnets[local.subnet_lookup["system"]].name) = {
      subscription_id      = data.azurerm_client_config.current.subscription_id
      resource_group_name  = azurerm_resource_group.rg.name
      virtual_network_name = module.network["aks"].name
    }
    (var.networks.aks.subnets[local.subnet_lookup["user"]].name) = {
      subscription_id      = data.azurerm_client_config.current.subscription_id
      resource_group_name  = azurerm_resource_group.rg.name
      virtual_network_name = module.network["aks"].name
    }
  }
}

/* module "container_registry" {
  source                       = "./modules/container_registry"
  name                         = var.acr_name
  resource_group_name          = azurerm_resource_group.rg.name
  region                     = var.region
  sku                          = var.acr_sku
  admin_enabled                = var.acr_admin_enabled
  georeplication_locations     = var.acr_georeplication_locations
  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
} */

module "aks_cluster" {
  source = "./modules/aks"

  name                    = var.aks_cluster_name
  dns_prefix              = lower(var.aks_cluster_name)
  region                = var.region
  resource_group_name     = azurerm_resource_group.rg.name
  resource_group_id       = azurerm_resource_group.rg.id
  private_cluster_enabled = var.aks_private_cluster
  vnet_subnet_id          = module.network["aks"].subnet_ids[var.networks.aks.subnets[local.subnet_lookup["system"]].name]

  default_node_pool_vm_size            = var.default_node_pool_vm_size
  default_node_pool_availability_zones = var.default_node_pool_availability_zones
  default_node_pool_max_count          = var.default_node_pool_max_count
  default_node_pool_min_count          = var.default_node_pool_min_count
  default_node_pool_node_count         = var.default_node_pool_node_count

  tags = var.tags

  network_dns_service_ip = var.network_dns_service_ip
  network_service_cidr   = var.network_service_cidr

  log_analytics_workspace_id = module.log_analytics_workspace.id

  tenant_id                 = data.azurerm_client_config.current.tenant_id
  admin_group_object_ids    = var.admin_group_object_ids
  ssh_public_key            = var.ssh_public_key
  workload_identity_enabled = var.workload_identity_enabled

  depends_on = [module.routetable]
}

/* 
Create RBAC
resource "azurerm_role_assignment" "network_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Network Contributor"
  principal_id         = module.aks_cluster.aks_identity_principal_id
  skip_service_principal_aad_check = true
} */

/* resource "azurerm_role_assignment" "acr_pull" {
  role_definition_name = "AcrPull"
  scope                = module.container_registry.id
  principal_id         = module.aks_cluster.kubelet_identity_object_id
  skip_service_principal_aad_check = true
}
 */
# Generate randon name for storage account
resource "random_string" "random_suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
  numeric = false
}

module "storage_account" {
  source = "./modules/storage_account"

  name                = lower("${var.aks_cluster_name}${random_string.random_suffix.result}sa")
  region            = var.region
  resource_group_name = azurerm_resource_group.rg.name
}

/* module "bastion_host" {
  source                       = "./modules/bastion_host"
  name                         = var.bastion_host_name
  region                     = var.region
  resource_group_name          = azurerm_resource_group.rg.name
  subnet_id                    = module.hub_network.subnet_ids["AzureBastionSubnet"]
  log_analytics_workspace_id   = module.log_analytics_workspace.id
  log_analytics_retention_days = var.log_analytics_retention_days
} */


/* module "node_pool" {
  source = "./modules/node_pool"
  resource_group_name = azurerm_resource_group.rg.name
  kubernetes_cluster_id = module.aks_cluster.id
  name                         = var.additional_node_pool_name
  vm_size                      = var.additional_node_pool_vm_size
  mode                         = var.additional_node_pool_mode
  node_labels                  = var.additional_node_pool_node_labels
  node_taints                  = var.additional_node_pool_node_taints
  availability_zones           = var.additional_node_pool_availability_zones
  vnet_subnet_id               = module.aks_network.subnet_ids[var.additional_node_pool_subnet_name]
  enable_auto_scaling          = var.additional_node_pool_enable_auto_scaling
  enable_host_encryption       = var.additional_node_pool_enable_host_encryption
  enable_node_public_ip        = var.additional_node_pool_enable_node_public_ip
  orchestrator_version         = var.kubernetes_version
  max_pods                     = var.additional_node_pool_max_pods
  max_count                    = var.additional_node_pool_max_count
  min_count                    = var.additional_node_pool_min_count
  node_count                   = var.additional_node_pool_node_count
  os_type                      = var.additional_node_pool_os_type
  priority                     = var.additional_node_pool_priority
  tags                         = var.tags

  depends_on                   = [module.routetable]
} */

module "key_vault" {
  source = "./modules/key_vault"
  name   = "${var.aks_cluster_name}-kv"

  region            = var.region
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
    (var.networks.hub.vnet_name) = {
      subscription_id     = data.azurerm_client_config.current.subscription_id
      resource_group_name = azurerm_resource_group.rg.name
    }
    (var.networks.aks.vnet_name) = {
      subscription_id     = data.azurerm_client_config.current.subscription_id
      resource_group_name = azurerm_resource_group.rg.name
    }
  }
}


/* module "acr_private_endpoint" {
  source                         = "./modules/private_endpoint"
  name                           = "${module.container_registry.name}PrivateEndpoint"
  region                       = var.region
  resource_group_name            = azurerm_resource_group.rg.name
  subnet_id                      = module.aks_network.subnet_ids[var.vm_subnet_name]
  tags                           = var.tags
  private_connection_resource_id = module.container_registry.id
  is_manual_connection           = false
  subresource_name               = "registry"
  private_dns_zone_group_name    = "AcrPrivateDnsZoneGroup"
  private_dns_zone_group_ids     = [module.acr_private_dns_zone.id]
} */

module "key_vault_private_endpoint" {
  source = "./modules/private_endpoint"

  name                           = "${title(module.key_vault.name)}PrivateEndpoint"
  region                       = var.region
  resource_group_name            = azurerm_resource_group.rg.name
  subnet_id                      = module.network["aks"].subnet_ids[var.networks.aks.subnets[local.subnet_lookup["vms"]].name]
  tags                           = var.tags
  private_connection_resource_id = module.key_vault.id
  subresource_name               = "vault"
  private_dns_zone_group_name    = "KeyVaultPrivateDnsZoneGroup"
  private_dns_zone_group_ids     = [module.private_dns_zones["KeyVaultPrivate"].id]
}

module "blob_private_endpoint" {
  source = "./modules/private_endpoint"

  name                           = "${title(module.storage_account.name)}PrivateEndpoint"
  region                       = var.region
  resource_group_name            = azurerm_resource_group.rg.name
  subnet_id                      = module.network["aks"].subnet_ids[var.networks.aks.subnets[local.subnet_lookup["vms"]].name]
  tags                           = var.tags
  private_connection_resource_id = module.storage_account.id
  subresource_name               = "blob"
  private_dns_zone_group_name    = "BlobPrivateDnsZoneGroup"
  private_dns_zone_group_ids     = [module.private_dns_zones["BlobPrivate"].id]
}