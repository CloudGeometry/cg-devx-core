
output "gitops_repo_git_clone_url" {
  value = module.gitops-repo.repo_git_clone_url
}

output "gitops_repo_html_url" {
  value = module.gitops-repo.repo_git_html_url
}

output "gitops_repo_ssh_clone_url" {
  value = module.gitops-repo.repo_git_ssh_clone_url
}

output "vcs_runner_token" {
  #This output is empty. It's here for vcs_gitlab module compatibility.
  value     = ""
  sensitive = true
}
