variable "oidc_endpoint" {
  type = string
}

variable "oidc_client_id" {
  type = string
}

variable "oidc_client_secret" {
  type      = string
  sensitive = true
}

variable "code_quality_admin_password" {
  type      = string
  sensitive = true
}

variable "code_quality_url" {
  type = string
}

variable "workloads" {
  description = "workloads harbor configuration"
  type        = map(object({
    description = optional(string, "")
  }))
  default = {}
}
