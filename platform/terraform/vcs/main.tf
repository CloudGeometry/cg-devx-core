terraform {
  # Remote backend configuration
  # <TF_VCS_REMOTE_BACKEND>
}

# Configure Git Provider
# <GIT_PROVIDER_MODULE>

locals {
  gitops_repo_name = "<GITOPS_REPOSITORY_NAME>"
  atlantis_url     = "https://<ATLANTIS_INGRESS_URL>/events"
  workload_enabled = false
  workload_repos   = local.workload_enabled == false ? {} : {
    "workload-demo-iac" = {
      atlantis_enabled             = true
      atlantis_url                 = local.atlantis_url
      atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
    },
    "workload-demo-template" = {
      is_template                  = true
    },
    "workload-demo" = {
    },
  }
}

module "vcs" {
  source = "../modules/vcs_<GIT_PROVIDER>"

  gitops_repo_name             = local.gitops_repo_name
  atlantis_url                 = local.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
  workload_repos               = local.workload_repos
}
