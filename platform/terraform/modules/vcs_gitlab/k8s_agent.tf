resource "gitlab_cluster_agent" "gitops" {
  project = module.gitops-repo.repo_id
  name    = "cc-cluster-agent"

  depends_on = [module.gitops-repo]
}

resource "gitlab_cluster_agent_token" "gitops" {
  project     = gitlab_cluster_agent.gitops.project
  agent_id    = gitlab_cluster_agent.gitops.agent_id
  name        = "cc-cluster-agent-token"
  description = "Token for the cc-cluster-agent"

  depends_on = [gitlab_cluster_agent.gitops]
}

# // Optionally, configure the agent as described in
# // https://docs.gitlab.com/ee/user/clusters/agent/install/index.html#create-an-agent-configuration-file
# resource "gitlab_repository_file" "gitops_agent_config" {
#   project   = module.gitops-repo.repo_id
#   branch    = "main"
#   file_path = ".gitlab/agents/${var.cluster_name}/config.yaml"
#   content = base64encode(<<CONTENT
# ci_access:
#   groups:
#     - id: ${var.vcs_owner}
#   CONTENT
#   )
#   commit_message = "Add agent config for ${var.cluster_name}"
# }
