locals {
  self_hosted_runners_repos = concat(
    [for workload in module.workload_repos : workload.repo_id],
  )
}

resource "gitlab_project_runner_enablement" "this" {
 for_each = module.workload_repos
  
  project   = each.value.repo_id
  runner_id = gitlab_user_runner.this.id
}
