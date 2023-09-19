variable "atlantis_repo_webhook_secret" {
  type    = string
  default = ""
}

variable "atlantis_url" {
  type    = string
  default = ""
}

variable "gitops_repo_name" {
  type    = string
  default = "gitops"
}

variable "vcs_bot_ssh_public_key" {
  type    = string
  default = ""
}

variable "demo_workload_enabled" {
  type    = bool
  default = false
}
