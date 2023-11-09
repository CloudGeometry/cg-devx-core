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

resource "azurerm_subnet" "public_subnet" {
  name                                          = "${local.vnet_name}-public"
  resource_group_name                           = azurerm_resource_group.rg.name
  virtual_network_name                          = azurerm_virtual_network.vnet.name
  address_prefixes                              = [cidrsubnet(var.cluster_network_cidr, 4, 0)]
  private_endpoint_network_policies_enabled     = false
  private_link_service_network_policies_enabled = true
}

resource "azurerm_subnet" "private_subnet" {
  name                                          = "${local.vnet_name}-private"
  resource_group_name                           = azurerm_resource_group.rg.name
  virtual_network_name                          = azurerm_virtual_network.vnet.name
  address_prefixes                              = [cidrsubnet(var.cluster_network_cidr, 4, 1)]
  private_endpoint_network_policies_enabled     = false
  private_link_service_network_policies_enabled = true
  service_endpoints                             = ["Microsoft.KeyVault", "Microsoft.Storage"]
}

resource "azurerm_subnet" "internal_subnet" {
  name                                          = "${local.vnet_name}-internal"
  resource_group_name                           = azurerm_resource_group.rg.name
  virtual_network_name                          = azurerm_virtual_network.vnet.name
  address_prefixes                              = [cidrsubnet(var.cluster_network_cidr, 4, 2)]
  private_endpoint_network_policies_enabled     = false
  private_link_service_network_policies_enabled = true
}


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


# private endpoints
resource "azurerm_private_endpoint" "key_vault_private_endpoint" {
  name                = "${title(azurerm_key_vault.key_vault.name)}PrivateEndpoint"
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private_subnet.id
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
  subnet_id           = azurerm_subnet.private_subnet.id
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
