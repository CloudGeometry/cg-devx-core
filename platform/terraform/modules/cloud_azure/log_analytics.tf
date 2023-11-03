resource "azurerm_log_analytics_workspace" "log_analytics_workspace" {
  name                = "${local.name}-law"
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