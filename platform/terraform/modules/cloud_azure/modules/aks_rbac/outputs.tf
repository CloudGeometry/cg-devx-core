output "app_client_id" {
  value       = azuread_application.appname.application_id
  description = "ID of current app client"
}

output "subscription_id" {
  value       = data.azurerm_client_config.current_subscription.subscription_id
  description = "Current azure subscription ID"
}
