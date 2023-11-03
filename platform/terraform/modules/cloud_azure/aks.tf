resource "azurerm_user_assigned_identity" "aks_identity" {
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.region
  tags                = local.tags

  name = "${local.name}Identity"

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                             = local.name
  location                         = var.region
  resource_group_name              = azurerm_resource_group.rg.name
  kubernetes_version               = var.cluster_version
  dns_prefix                       = lower(local.name)
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
    vnet_subnet_id         = azurerm_subnet.private_subnet.id
    # pod_subnet_id          = [] ?? do we need it
    zones                  = local.azs
    node_labels            = var.cluster_node_labels
    enable_auto_scaling    = true
    enable_host_encryption = false
    enable_node_public_ip  = false
    node_count             = local.default_node_group.desired_size
    min_count              = local.default_node_group.min_size
    max_count              = local.default_node_group.max_size
    max_pods               = local.max_pods
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

  # may need to enable this
  # http_proxy_config {
  #   no_proxy = azurerm_subnet.private_subnet.address_prefixes
  # }

  lifecycle {
    ignore_changes = [
      kubernetes_version,
      tags,
      # node_count is still affected by issue https://github.com/hashicorp/terraform-provider-azurerm/issues/14522
      # ignore changes as workaround
      default_node_pool.0.node_count
    ]
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "node_pool" {
  for_each = {for pool in local.additional_node_pools : pool["name"] => pool}

  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id

  name                  = each.key
  vm_size               = each.value.instance_types
  zones                 = local.azs
  vnet_subnet_id        = azurerm_subnet.private_subnet.id
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
