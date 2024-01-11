output "app_client_id" {
  value       = azurerm_user_assigned_identity.aks_workload_identity.client_id
  description = "ID of client"
}
