module "gitops-repo" {
  source = "./repository"

  repo_name                    = var.gitops_repo_name
  archive_on_destroy           = false
  atlantis_enabled             = true
  atlantis_url                 = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  cd_webhook_url               = var.cd_webhook_url
  cd_webhook_secret            = var.cd_webhook_secret
  vcs_subscription_plan        = var.vcs_subscription_plan
  vcs_owner                    = data.gitlab_group.owner.group_id
  branch_protection            = true
}
