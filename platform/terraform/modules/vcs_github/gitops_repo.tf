module "gitops-repo" {
  source = "./repository"

  repo_name          = var.gitops_repo_name
  archive_on_destroy = false
  atlantis_enabled   = true
  atlantis_url       = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret

}

output "gitops_repo_git_clone_url" {
  value = module.gitops-repo.repo_git_clone_url
}

output "gitops_repo_html_url" {
  value = module.gitops-repo.repo_git_html_url
}

output "gitops_repo_ssh_clone_url" {
  value = module.gitops-repo.repo_git_ssh_clone_url
}
