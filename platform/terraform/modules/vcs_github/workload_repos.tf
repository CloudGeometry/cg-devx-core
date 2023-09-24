module "workload_repos" {
  source    = "./repository"
  for_each = var.workload_repos

  repo_name          = each.key
  description        = each.value.description
  visibility         = each.value.visibility
  auto_init          = each.value.auto_init
  archive_on_destroy = each.value.archive_on_destroy
  has_issues         = each.value.has_issues
  is_template        = each.value.is_template
  default_branch_name = each.value.default_branch_name
  delete_branch_on_merge = each.value.delete_branch_on_merge
  template                     = each.value.template
  atlantis_enabled             = each.value.atlantis_enabled
  atlantis_url                 = each.value.atlantis_url
  atlantis_repo_webhook_secret = each.value.atlantis_repo_webhook_secret
}
