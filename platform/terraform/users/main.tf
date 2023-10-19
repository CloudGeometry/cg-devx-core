terraform {
  # Remote backend configuration
  # <TF_USERS_REMOTE_BACKEND>
}

# Configure Git Provider
# <GIT_PROVIDER_MODULE>

provider "vault" {
  skip_tls_verify = "true"
}

locals {
  gitops_repo_name = "<GITOPS_REPOSITORY_NAME>"
  bot_vcs_username = "<GIT_USER_NAME>"
  bot_email        = "<OWNER_EMAIL>"
  oidc_groups      = {
### system groups
    "admins"                = {
    },
    "developers"            = {
    },
### Workload groups definition bellow
    # "workload-demo-admins"  = {
    # },
    # "workload-demo-developers"  = {
    # },
  }
  users = {
### Primary bot user
    "cgdevx-bot" = {
      vcs_username   = local.bot_vcs_username
      email             = local.bot_email
      first_name        = "CG DevX"
      last_name         = "Bot"
      vcs_team_slugs = ["${local.gitops_repo_name}-admins"]
      acl_policies      = ["admin", "default"]
      oidc_groups_for_user = ["admins"]
    },
### Additional users defined bellow. Use this as an example
    # "cgdevx-demobot-2" = {
    #   vcs_username   = "cgdevx-demobot-2"
    #   email             = "demobot2@cloudgeometry.io"
    #   first_name        = "Second"
    #   last_name         = "Bot"
    #   vcs_team_slugs = ["${local.gitops_repo_name}-maintainers", "workload-demo-admins"]
    #   acl_policies      = ["developers", "default", "workload-demo-admins"]
    #   oidc_groups_for_user = ["developers", "workload-demo-admins"]
    # },
  }
}

module "users" {
  source           = "../modules/users_<GIT_PROVIDER>"
  users            = local.users
  oidc_groups      = local.oidc_groups
}
