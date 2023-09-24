variable "atlantis_repo_webhook_secret" {
  type    = string
  default = ""
  sensitive   = true
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

variable "workload_repos" {
  description = "workloads repos configuration"
  type = map(object({
    description                  = optional(string, "")
    visibility                   = optional(string, "private")
    auto_init                    = optional(bool, false)
    archive_on_destroy           = optional(bool, false)
    has_issues                   = optional(bool, false)
    is_template                  = optional(bool, false)
    default_branch_name          = optional(string, "main")
    delete_branch_on_merge       = optional(bool, true)
    template                     = optional(map(string), {})
    atlantis_enabled             = optional(bool, false)
    atlantis_url                 = optional(string, "")
    atlantis_repo_webhook_secret = optional(string, "")
    }))
  default = {}
}
