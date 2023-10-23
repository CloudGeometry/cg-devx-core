variable "artifact_registry_oidc_client_id" {
  type = string
}

variable "artifact_registry_oidc_client_secret" {
  type = string
}

variable "workloads" {
  description = "workloads configuration"
  type = map(object({
    description                  = optional(string, "")
    }))
  default = {}
}