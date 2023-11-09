variable "app_name" {
  description = "oidc application name"
  type        = string
}

variable "identity_group_ids" {
  description = "list of identity group ids"
  type        = list(string)
}

variable "oidc_provider_key_name" {
  description = "oidc provider key name"
  type        = string
}

variable "redirect_uris" {
  description = "list of redirect urls"
  type        = list(string)
}

variable "secret_mount_path" {
  description = "vault path for stiring oidc secrets"
  type        = string
}