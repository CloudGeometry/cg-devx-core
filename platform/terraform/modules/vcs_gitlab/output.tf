
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
  value = gitlab_user_runner.group_runner.token
  sensitive = true
}

output "vcs_k8s_agent_token" {
  value = gitlab_cluster_agent_token.gitops.token
  sensitive = true
}
