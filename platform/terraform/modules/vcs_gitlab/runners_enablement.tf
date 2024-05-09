# Commented untill we are figured out if we need it or not

# resource "gitlab_project_runner_enablement" "this" {
#   for_each = module.workload_repos

#   project   = each.value.repo_id
#   runner_id = gitlab_user_runner.this.id
# }
