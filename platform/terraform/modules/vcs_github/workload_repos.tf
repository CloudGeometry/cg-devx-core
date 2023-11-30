module "workload_repos" {
  source   = "./repository"
  for_each = {
    for r in flatten([
      for wl in var.workloads :
      [for k, v in wl.repos : { k = k, v = v }]
    ]) : r.k => r.v
  }

  repo_name                    = each.key
  description                  = each.value.description
  visibility                   = each.value.visibility
  auto_init                    = each.value.auto_init
  archive_on_destroy           = each.value.archive_on_destroy
  has_issues                   = each.value.has_issues
  default_branch_name          = each.value.default_branch_name
  delete_branch_on_merge       = each.value.delete_branch_on_merge
  atlantis_enabled             = each.value.atlantis_enabled
  atlantis_url                 = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
}
