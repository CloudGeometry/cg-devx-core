terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.50"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.23.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.11.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}


resource "azurerm_user_assigned_identity" "aks_identity" {
  resource_group_name = var.resource_group_name
  location            = var.region
  tags                = var.tags

  name = "${var.name}Identity"

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

data "azurerm_client_config" "current_subscription" {}

output "subscription_id" {
  value = data.azurerm_client_config.current_subscription.subscription_id
}

resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                             = var.name
  location                         = var.region
  resource_group_name              = var.resource_group_name
  kubernetes_version               = var.cluster_version
  dns_prefix                       = var.dns_prefix
  private_cluster_enabled          = var.private_cluster_enabled
  automatic_channel_upgrade        = var.automatic_channel_upgrade
  sku_tier                         = var.sku_tier
  workload_identity_enabled        = var.workload_identity_enabled
  oidc_issuer_enabled              = var.oidc_issuer_enabled
  open_service_mesh_enabled        = var.open_service_mesh_enabled
  image_cleaner_enabled            = var.image_cleaner_enabled
  azure_policy_enabled             = var.azure_policy_enabled
  http_application_routing_enabled = var.http_application_routing_enabled

  default_node_pool {
    name                   = var.default_node_pool_name
    vm_size                = var.default_node_pool_vm_size
    vnet_subnet_id         = var.vnet_subnet_id
    pod_subnet_id          = var.pod_subnet_id
    zones                  = var.default_node_pool_availability_zones
    node_labels            = var.default_node_pool_node_labels
    node_taints            = var.default_node_pool_node_taints
    enable_auto_scaling    = var.default_node_pool_enable_auto_scaling
    enable_host_encryption = var.default_node_pool_enable_host_encryption
    enable_node_public_ip  = var.default_node_pool_enable_node_public_ip
    max_pods               = var.default_node_pool_max_pods
    max_count              = var.default_node_pool_max_count
    min_count              = var.default_node_pool_min_count
    node_count             = var.default_node_pool_node_count
    os_disk_type           = var.default_node_pool_os_disk_type
    tags                   = var.tags
  }

  linux_profile {
    admin_username = var.admin_username
    ssh_key {
      key_data = var.ssh_public_key
    }
  }

  identity {
    type         = "UserAssigned"
    identity_ids = tolist([azurerm_user_assigned_identity.aks_identity.id])
  }

  network_profile {
    dns_service_ip    = var.network_dns_service_ip
    network_plugin    = var.network_plugin
    outbound_type     = var.outbound_type
    service_cidr      = var.network_service_cidr
    load_balancer_sku = "standard"
  }

  oms_agent {
    msi_auth_for_monitoring_enabled = true
    log_analytics_workspace_id      = coalesce(var.oms_agent.log_analytics_workspace_id, var.log_analytics_workspace_id)
  }

  dynamic "ingress_application_gateway" {
    for_each = try(var.ingress_application_gateway.gateway_id, null) == null ? [] : [1]

    content {
      gateway_id  = var.ingress_application_gateway.gateway_id
      subnet_cidr = var.ingress_application_gateway.subnet_cidr
      subnet_id   = var.ingress_application_gateway.subnet_id
    }
  }

  azure_active_directory_role_based_access_control {
    managed                = true
    tenant_id              = var.tenant_id
    admin_group_object_ids = var.admin_group_object_ids
    azure_rbac_enabled     = var.azure_rbac_enabled
  }


  lifecycle {
    ignore_changes = [
      kubernetes_version,
      tags
    ]
  }
}


## AKS service account part. 
locals {
  namespace_name = "atlantis"
  ## This should match the name of the service account created by helm chart
  service_account_name = "sa-atlantis-${var.resource_group_name}"
}

## Azure AD application that represents the app
resource "azuread_application" "atlantis" {
  display_name = "sp-atlantis-${var.resource_group_name}"
}

resource "azuread_service_principal" "atlantis" {
  application_id = azuread_application.atlantis.application_id
}

resource "azuread_service_principal_password" "atlantis" {
  service_principal_id = azuread_service_principal.atlantis.id
}

## Azure AD federated identity used to federate kubernetes with Azure AD
resource "azuread_application_federated_identity_credential" "aks-atlantis-id" {
  application_object_id = azuread_application.atlantis.object_id
  display_name          = "fed-identity-aks-atlantis-id-${var.resource_group_name}"
  description           = "The federated identity used to federate aks-atlantis-id with Azure AD with the app service running in k8s ${var.resource_group_name}"
  audiences             = ["api://AzureADTokenExchange"]
  issuer                = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
  subject               = "system:serviceaccount:${local.namespace_name}:${local.service_account_name}"
  depends_on =  [azurerm_kubernetes_cluster.aks_cluster]
}

output "app_client_id" {
  value = azuread_application.atlantis.application_id
}


## Role assignment to the application
resource "azurerm_role_assignment" "contributor" {
  scope                = "/subscriptions/${data.azurerm_client_config.current_subscription.subscription_id}/resourceGroups/${var.resource_group_name}"
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.atlantis.id
}


/* resource "azurerm_monitor_diagnostic_setting" "settings" {
  name                       = "DiagnosticsSettings"
  target_resource_id         = azurerm_kubernetes_cluster.aks_cluster.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "kube-apiserver"

    retention_policy {
      enabled = true  
    }
  }

  enabled_log {
    category = "kube-audit"

    retention_policy {
      enabled = true
    }
  }

  enabled_log {
    category = "kube-audit-admin"

    retention_policy {
      enabled = true
    }
  }

  enabled_log {
    category = "kube-controller-manager"

    retention_policy {
      enabled = true
    }
  }

  enabled_log {
    category = "kube-scheduler"

    retention_policy {
      enabled = true
    }
  }

  enabled_log {
    category = "cluster-autoscaler"

    retention_policy {
      enabled = true
    }
  }

  enabled_log {
    category = "guard"

    retention_policy {
      enabled = true
    }
  }

  metric {
    category = "AllMetrics"

    retention_policy {
      enabled = true
    }
  }
} */