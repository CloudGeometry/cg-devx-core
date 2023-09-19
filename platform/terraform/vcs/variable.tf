variable "atlantis_repo_webhook_secret" {
  type    = string
  default = ""
}

variable "vcs_bot_ssh_public_key" {
  type    = string
  default = ""
}

variable "demo_workload_enabled" {
  type    = bool
  default = false
}
