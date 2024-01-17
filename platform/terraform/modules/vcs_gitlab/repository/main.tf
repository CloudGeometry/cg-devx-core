terraform {

  required_providers {
    gitlab = {
      # https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs
      source = "gitlabhq/gitlab"
      version = "16.7.0"
    }
  }
}


# Configure Git Provider
provider "gitlab" {

}
resource "gitlab_project" "repo" {
  name        = var.repo_name
  description = var.description

  visibility_level                 = var.visibility
  initialize_with_readme           = var.auto_init
  archive_on_destroy               = var.archive_on_destroy
  issues_enabled                   = var.has_issues
  remove_source_branch_after_merge = var.delete_branch_on_merge
  namespace_id = var.vcs_owner

  #Didn't find the correct option to enable/disable merge commits in gitlab
  #allow_merge_commit     = var.allow_merge_commit

  # atlantis currently doesn't support branch protection with required linear historyw when repo settings allowed merge commits
  # need to monitor these issues
  # https://github.com/runatlantis/atlantis/issues/1176
  # https://github.com/runatlantis/atlantis/pull/3211
  # https://github.com/runatlantis/atlantis/pull/3276
  # https://github.com/runatlantis/atlantis/pull/3321

  # Didn't find option to enable templating in gitlab 
  # dynamic "template" {
  #   for_each = length(var.template) != 0 ? [var.template] : []

  #   content {
  #     owner      = lookup(template.value, "owner", null)
  #     repository = lookup(template.value, "repository", null)
  #   }
  # }

}

# Protect the main branch of the repository. Additionally, require 
# only allow the engineers team merge to the branch.

resource "gitlab_branch_protection" "this" {
  count   = var.branch_protection && var.vcs_subscription_plan ? 1 : 0
  project = gitlab_project.repo.id

  branch           = "main"
  allow_force_push = false
}

data "gitlab_group" "owner" {
  group_id = var.vcs_owner
}

output "repo_name" {
  value = gitlab_project.repo.name
}

output "repo_git_clone_url" {
  value = gitlab_project.repo.ssh_url_to_repo
}

output "repo_git_html_url" {
  value = gitlab_project.repo.http_url_to_repo
}

# There is no attribute for gitlab project that returns url for anonynous git clone
# than the same attribute ssh_url_to_repo is used
output "repo_git_ssh_clone_url" {
  value = gitlab_project.repo.ssh_url_to_repo
}

output "repo_id" {
  value = gitlab_project.repo.id
}
