terraform {
  # Remote backend configuration
  # <TF_VCS_REMOTE_BACKEND>
  required_providers {
    # <GIT_REQUIRED_PROVIDER>
  }
}

# Configure Git Provider
# <GIT_PROVIDER_MODULE>


locals {
  gitops_repo_name      = "<GITOPS_REPOSITORY_NAME>"
  atlantis_url          = "https://<IAC_PR_AUTOMATION_INGRESS_URL>/events"
  cd_webhook_url        = "https://<CD_INGRESS_URL>/api/webhook"
  cluster_name          = "<PRIMARY_CLUSTER_NAME>"
  vcs_owner             = "<GIT_ORGANIZATION_NAME>"
  vcs_subscription_plan = <GIT_SUBSCRIPTION_PLAN> # bool true(paid plans) / false (free tier)
}


module "vcs" {
  source = "../modules/vcs_<GIT_PROVIDER>"

  gitops_repo_name             = local.gitops_repo_name
  atlantis_url                 = local.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  cd_webhook_url               = local.cd_webhook_url
  cd_webhook_secret            = var.cd_webhook_secret
  vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
  workloads                    = var.workloads
  cluster_name                 = local.cluster_name
  vcs_owner                    = local.vcs_owner
  vcs_subscription_plan        = local.vcs_subscription_plan
}
