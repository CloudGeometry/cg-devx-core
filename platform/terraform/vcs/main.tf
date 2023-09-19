terraform {
  # Remote backend configuration
  # <TF_VCS_REMOTE_BACKEND>
}

# Configure Git Provider
# <GIT_PROVIDER_MODULE>

locals {
  gitops_repo_name = "<GITOPS_REPOSITORY_NAME>"
  atlantis_url     = "https://<ATLANTIS_INGRESS_URL>/events"
}

module "vcs" {
  source = "../modules/vcs_<GIT_PROVIDER>"

  gitops_repo_name             = local.gitops_repo_name
  atlantis_url                 = local.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
  demo_workload_enabled        = var.demo_workload_enabled
}
