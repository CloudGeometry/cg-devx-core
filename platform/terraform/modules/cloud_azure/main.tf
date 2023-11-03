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
  name                         = var.cluster_name
  vnet_name                    = "${var.cluster_name}-vnet"
  log_analytics_retention_days = 30
  tags                         = {
    cgx_name = var.cluster_name
  }
  azs                   = [for i in range(1, var.az_count + 1) : tostring(i)]
  default_node_group    = var.node_groups[0]
  additional_node_pools = try(slice(var.node_groups, 1, length(var.node_groups)), [])
  max_pods              = 100
  node_admin_username   = "azadmin"
}

resource "azurerm_resource_group" "rg" {
  name     = "${local.name}-rg"
  location = var.region
  tags     = local.tags
}

data "http" "runner_ip_address" {
  url = "https://icanhazip.com"
}
