variable "users" {
  description = "vault users"
  type = map(object({
    user_disabled                = optional(bool, false)
    vcs_username              = optional(string, "")
    email                        = optional(string, "")
    first_name                   = optional(string, "")
    last_name                    = optional(string, "")
    vcs_team_slugs            = optional(list(string), [])
    acl_policies                 = optional(list(string), ["admin", "default"])
    oidc_groups_for_user         = optional(list(string), ["developers"])
  }))
  default = {}
}

variable "oidc_groups" {
  description = "vault groups configuration"
  type = map(object({
    description = optional(string, "")
  }))
  default = {
    "admins"                = {
    },
    "developers"            = {
    },
  }
}
