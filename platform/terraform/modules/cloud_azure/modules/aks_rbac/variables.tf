variable "resource_group_name" {
  description = "(Required) Specifies the name of the resource group."
  type        = string
}

variable "name" {
  description = "(Required) Specifies the name of the resource group."
  type        = string
}

/* variable "service_accounts" {
  description = "(Required) Specifies the name of the node pool."
  type        = map(any)
} */


/* variable "service_account_name" {
  description = "(Required) Specifies the name of the node pool."
  type        = string
}
 */
variable "role_definition_name" {
  description = "(Required) Specifies the name of the node pool."
  type        = string
}

variable "oidc_issuer_url" {
  description = "OIDC url for Azure Kubernetes Managed Cluster"
  type        = string
}