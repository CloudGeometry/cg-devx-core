variable "code_quality_oidc_client_id" {
  type = string
}

variable "code_quality_oidc_client_secret" {
  type      = string
  sensitive = true
}

variable "code_quality_admin_password" {
  type      = string
  sensitive = true
}

variable "registry_oidc_client_id" {
  type = string
}

variable "registry_oidc_client_secret" {
  type      = string
  sensitive = true
}

variable "registry_main_robot_password" {
  type      = string
  sensitive = true
}
