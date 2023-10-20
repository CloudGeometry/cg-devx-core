variable "oidc_endpoint" {
  type = string
}

variable "oidc_client_id" {
  type = string
}

variable "oidc_client_secret" {
  type = string
}

variable "workloads" {
  description = "workloads harbor configuration"
  type = map(object({
    description  = optional(string, "")
    }))
  default = {}
}
