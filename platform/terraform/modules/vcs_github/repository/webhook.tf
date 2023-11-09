resource "github_repository_webhook" "gitops_atlantis_webhook" {
  count      = var.atlantis_enabled ? 1 : 0
  repository = github_repository.repo.name

  configuration {
    content_type = "json"
    insecure_ssl = false
    url          = var.atlantis_url
    secret       = var.atlantis_repo_webhook_secret
  }

  active = true

  events = ["pull_request_review", "push", "issue_comment", "pull_request"]
}
