output "app_client_id" {
  value       = azuread_application.appname.application_id
  description = "ID of current app client"
}
