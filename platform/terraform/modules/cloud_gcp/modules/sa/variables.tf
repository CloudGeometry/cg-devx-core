variable "service_account_name" {
  description = "The name of the service account in Google."
  type        = string
}

variable "kubernetes_service_accounts" {
  description = "List of Kubernetes service accounts to map to GCP service account"
  type        = list(object({
    namespace = string
    name      = string
  }))
}

variable "display_name" {
  description = "Display name (description) for the service account."
  type        = string
}

variable "project" {
  description = "Google Project ID"
  type        = string
}

variable "roles" {
  description = "A list of roles to assign to the service account."
  type        = list(string)
}

variable "create_service_account_key" {
  description = ""
  type        = bool

  default = false
}

variable "keyring" {
  description = ""
  type        = string

  default = ""
}

variable "create_bucket_iam_access" {
  description = ""
  type        = bool

  default = false
}

variable "bucket_name" {
  description = ""
  type        = string

  default = ""
}
