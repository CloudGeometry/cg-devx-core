terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
}

resource "azurerm_user_assigned_identity" "aks_workload_identity" {
  location            = var.resource_group_location
  name                = "${var.name}-aks-workload-identity"
  resource_group_name = var.resource_group_name
}

resource "azurerm_federated_identity_credential" "workload_identity_credentials" {
  audience            = ["api://AzureADTokenExchange"]
  issuer              = var.oidc_issuer_url
  name                = "${var.name}-workload-identity-credentials"
  parent_id           = azurerm_user_assigned_identity.aks_workload_identity.id
  resource_group_name = var.resource_group_name
  subject             = "system:serviceaccount:${var.namespace}:${var.service_account_name}"

  depends_on = [azurerm_user_assigned_identity.aks_workload_identity]
}

data "azurerm_client_config" "current_subscription" {}

resource "azurerm_role_assignment" "aks_rbac" {
  count = length(var.role_definitions)

  scope                = "/subscriptions/${data.azurerm_client_config.current_subscription.subscription_id}${var.role_definitions[count.index].scope}"
  role_definition_name = var.role_definitions[count.index].name
  principal_id         = azurerm_user_assigned_identity.aks_workload_identity.principal_id
}
