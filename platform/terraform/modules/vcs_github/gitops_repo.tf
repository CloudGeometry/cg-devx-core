module "gitops-repo" {
  source = "./repository"

  repo_name          = var.gitops_repo_name
  archive_on_destroy = false
  atlantis_enabled   = true
  atlantis_url       = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret

}