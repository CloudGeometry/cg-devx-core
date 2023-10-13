variable "cluster_name" {
  description = "primary cluster name"
  default = ""
  type = string

}

variable "gitops_repo_name" {
  description = "main gitops repositoy name"
  type = string
}


variable "bot_vcs_username" {
  description = "cgdevx-bot github username"
  type = string
}

variable "bot_email" {
  description = "cgdevx-bot email"
  type = string
}

variable "additional_users" {
  description = "workloads users"
  type = map(object({
    description = optional(string, "")
    }))
  default = {}
}

variable "workloads" {
  description = "workloads configuration"
  type = map(object({
    description                  = optional(string, "")
    }))
  default = {}
}
