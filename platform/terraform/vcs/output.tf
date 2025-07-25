output "gitops_repo_git_clone_url" {
  value = module.vcs.gitops_repo_git_clone_url
}

output "gitops_repo_html_url" {
  value = module.vcs.gitops_repo_html_url
}

output "gitops_repo_ssh_clone_url" {
  value = module.vcs.gitops_repo_ssh_clone_url
}

output "vcs_runner_token" {
  value = module.vcs.vcs_runner_token
  sensitive = true
}

output "vcs_k8s_agent_token" {
  value = module.vcs.vcs_k8s_agent_token
  sensitive = true
}
