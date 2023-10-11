variable "resource_group_name" {
  description = "(Required) Specifies the name of the resource group."
  type        = string
}

variable "name" {
  description = "(Required) Specifies the name of the resource group."
  type        = string
}

variable "namespace" {
  description = "(Required) Specifies the name of the namespace."
  type        = string
}

variable "service_account_name" {
  description = "(Required) Specifies the name of the service account."
  type        = string
}

variable "role_definitions" {
  description = "(Required) Specifies the name of the node pool."
  type        = list(any)
}

variable "oidc_issuer_url" {
  description = "OIDC url for Azure Kubernetes Managed Cluster"
  type        = string
}


