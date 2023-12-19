locals {
  self_hosted_runners_repos = concat(
    [for workload in module.workload_repos : workload.repo_id], 
    [module.gitops-repo.repo_id]
  )
}

resource "github_actions_runner_group" "this" {
  count = var.vcs_subscription_plan ? 1 : 0
  name                    = var.vcs_owner
  visibility              = "selected"
  selected_repository_ids = local.self_hosted_runners_repos
}
