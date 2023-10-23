terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }

  required_version = ">= 0.14.9"
}

resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = var.address_space
  location            = var.region
  resource_group_name = var.resource_group_name
  tags                = var.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

# resource "azurerm_subnet" "subnet" {
#   for_each = { for subnet in var.subnets : subnet.name => subnet }

#   name                                          = each.key
#   resource_group_name                           = var.resource_group_name
#   virtual_network_name                          = azurerm_virtual_network.vnet.name
#   address_prefixes                              = each.value.address_prefixes
#   private_endpoint_network_policies_enabled     = each.value.private_endpoint_network_policies_enabled
#   private_link_service_network_policies_enabled = each.value.private_link_service_network_policies_enabled
# }

resource "azurerm_subnet" "subnet" {
  count = length(var.subnets)

  name                                          = "${var.vnet_name}-${var.subnets[count.index]}"
  resource_group_name                           = var.resource_group_name
  virtual_network_name                          = azurerm_virtual_network.vnet.name
  address_prefixes                              = [cidrsubnet(var.address_space[0], 4, count.index)]
  private_endpoint_network_policies_enabled     = true
  private_link_service_network_policies_enabled = false

}

/* resource "azurerm_monitor_diagnostic_setting" "settings" {
  name                       = "DiagnosticsSettings"
  target_resource_id         = azurerm_virtual_network.vnet.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  log {
    category = "VMProtectionAlerts"
    enabled  = true

    retention_policy {
      enabled = true
      days    = var.log_analytics_retention_days
    }
  }

  metric {
    category = "AllMetrics"

    retention_policy {
      enabled = true
      days    = var.log_analytics_retention_days
    }
  }
} */