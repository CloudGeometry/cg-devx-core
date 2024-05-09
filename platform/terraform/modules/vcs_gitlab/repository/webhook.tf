resource "gitlab_project_hook" "gitops_atlantis_webhook" {
  count   = var.atlantis_enabled ? 1 : 0
  project = gitlab_project.repo.id


  url                     = var.atlantis_url
  enable_ssl_verification = true
  token                   = var.atlantis_repo_webhook_secret

  merge_requests_events = true
  push_events           = true
  note_events           = true

}
