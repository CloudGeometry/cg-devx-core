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
  vcs_bot_username = "<GIT_USER_NAME>"
  bot_email        = "<OWNER_EMAIL>"
  workload_enabled = false
  workloads        = local.workload_enabled == false ? {} : {
    "workload-demo" = {
    },
    "workload-demo2" = {
    },
    "workload-demo3" = {
    },
  }
  additional_users_enabled = false
  additional_users         = local.additional_users_enabled == false ? {} : {
    "cgdevx-demobot-2" = {
    },
    "cgdevx-demobot-3" = {
    },
  }
}


module "users" {
  source           = "../modules/users_<GIT_PROVIDER>"
  gitops_repo_name = local.gitops_repo_name
  vcs_bot_username = local.vcs_bot_username
  bot_email        = local.bot_email
  additional_users = local.additional_users
  workloads        = local.workloads
}


