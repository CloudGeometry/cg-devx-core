variable "repo_name" {
  type = string
}

variable "description" {
  type    = string
  default = ""
}

variable "visibility" {
  type    = string
  default = "private"
}

variable "auto_init" {
  type    = bool
  default = false
}

variable "archive_on_destroy" {
  type    = bool
  default = false
}

variable "has_issues" {
  type    = bool
  default = false
}

variable "default_branch_name" {
  type    = string
  default = "main"
}

variable "delete_branch_on_merge" {
  type    = bool
  default = true
}

variable "branch_protection" {
  type    = bool
  default = true
}

variable "allow_merge_commit" {
  type    = bool
  default = false
}

variable "template" {
  type        = map(string)
  description = "Template Repository object for Repository creation"
  default     = {}
}

variable "atlantis_enabled" {
  type    = bool
  default = false
}

variable "atlantis_url" {
  type    = string
  default = ""
}

variable "atlantis_repo_webhook_secret" {
  type      = string
  default   = ""
  sensitive = true
}

variable "cd_webhook_secret" {
  type      = string
  default   = ""
  sensitive = true
}

variable "cd_webhook_url" {
  type    = string
  default = ""
}

variable "vcs_subscription_plan" {
  description = "True for advanced github/gitlab plan. False for free tier"
  type        = bool
  default     = false
}
