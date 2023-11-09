terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
}

data "azurerm_client_config" "current_subscription" {}

## Azure AD application that represents the app
resource "azuread_application" "appname" {
  display_name = var.name
}

resource "azuread_service_principal" "sp_name" {
  application_id = azuread_application.appname.application_id
}

resource "azuread_service_principal_password" "asp_pass" {
  service_principal_id = azuread_service_principal.sp_name.id
}

## Azure AD federated identity used to federate kubernetes with Azure AD
resource "azuread_application_federated_identity_credential" "aks-app-id" {
  application_object_id = azuread_application.appname.object_id
  display_name          = "fed-identity-aks-id-${var.service_account_name}"
  description           = "The federated identity used to federate ${var.service_account_name} with Azure AD with the app service running in k8s in ${var.resource_group_name}"
  audiences             = ["api://AzureADTokenExchange"]
  issuer                = var.oidc_issuer_url
  subject               = "system:serviceaccount:${var.namespace}:${var.service_account_name}"
}


## Role assignment to the application
resource "azurerm_role_assignment" "aks_rbac" {
  count = length(var.role_definitions)

  scope                = "/subscriptions/${data.azurerm_client_config.current_subscription.subscription_id}${var.role_definitions[count.index].scope}"
  role_definition_name = var.role_definitions[count.index].name
  principal_id         = azuread_service_principal.sp_name.id
}
