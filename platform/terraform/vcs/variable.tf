variable "atlantis_repo_webhook_secret" {
  type    = string
  default = ""
}

variable "argocd_webhook_secret" {
  type    = string
  default = ""
}

variable "vcs_bot_ssh_public_key" {
  type    = string
  default = ""
}

variable "workloads" {
  description = "Workloads configuration"
  type = map(object({
    description = optional(string, "")
    repos = map(object({
      description            = optional(string, "")
      visibility             = optional(string, "private")
      auto_init              = optional(bool, false)
      archive_on_destroy     = optional(bool, false)
      has_issues             = optional(bool, false)
      default_branch_name    = optional(string, "main")
      delete_branch_on_merge = optional(bool, true)
      branch_protection      = optional(bool, true)
      atlantis_enabled       = optional(bool, false)
    }))
  }))
  default = {}
}
