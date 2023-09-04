terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }

  required_version = ">= 0.14.9"
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
/* 
resource "azurerm_public_ip" "aks_lb_pip" {
  name                = "${var.name}-lb-pip"
  location            = var.region
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
}

resource "azurerm_lb" "aks_lb" {
  name                = "${var.name}-lb"
  location            = var.region
  resource_group_name = var.resource_group_name

  frontend_ip_configuration {
    name                 = "${var.name}-lb-pip"
    public_ip_address_id = azurerm_public_ip.aks_lb_pip.id
  }
}



resource "azurerm_lb_probe" "aks_lb_probe" {
  name                       = "${var.name}-lb-probe"
  resource_group_name        = var.resource_group_name
  loadbalancer_id            = azurerm_lb.aks_lb.id
  protocol                   = "TCP"
  port                       = 80
  interval_in_seconds        = 15
  number_of_probes           = 2
}

resource "azurerm_lb_backend_address_pool" "aks_lb_backend_pool" {
  name                = "${var.name}-aks_pool"
  resource_group_name = var.resource_group_name
  loadbalancer_id     = azurerm_lb.aks_lb.id
  backend_addresses = [
    {
      ip_address = "10.0.0.5" 
    },
  ]

  probe {
    id = azurerm_lb_probe.aks_lb_probe.id
  }
}
 */
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