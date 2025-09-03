terraform {

  required_providers {
    gitlab = {
      # https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs
      source  = "gitlabhq/gitlab"
      version = "<GITLAB_PROVIDER_VERSION>"
    }
  }
}

data "gitlab_current_user" "current" {}

resource "gitlab_project" "repo" {
  name        = var.repo_name
  description = var.description

  default_branch                   = var.default_branch_name
  visibility_level                 = var.visibility
  initialize_with_readme           = var.auto_init
  archive_on_destroy               = var.archive_on_destroy
  issues_enabled                   = var.has_issues
  remove_source_branch_after_merge = var.delete_branch_on_merge
  namespace_id                     = var.vcs_owner
  # disable shared runners and force usage of group runners provided by the platform
  shared_runners_enabled = false


  # atlantis currently doesn't support branch protection with required linear history when repo settings allowed merge commits
  # need to monitor these issues
  # https://github.com/runatlantis/atlantis/issues/1176
  # https://github.com/runatlantis/atlantis/pull/3211
  # https://github.com/runatlantis/atlantis/pull/3276
  # https://github.com/runatlantis/atlantis/pull/3321

}

# Protect the main branch of the repository. Additionally, require
# only allow the engineers team merge to the branch.

resource "gitlab_branch_protection" "this" {
  count   = var.branch_protection ? 1 : 0
  project = gitlab_project.repo.id

  branch           = var.default_branch_name
  allow_force_push = false

  dynamic "allowed_to_push" {
    for_each = var.vcs_subscription_plan && var.allow_push_to_protected ? [1] : []

    content {
      user_id = data.gitlab_current_user.current.id
    }

  }
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

# There is no attribute for gitlab project that returns url for anonymous git clone
# than the same attribute ssh_url_to_repo is used
output "repo_git_ssh_clone_url" {
  value = gitlab_project.repo.ssh_url_to_repo
}

output "repo_id" {
  value = gitlab_project.repo.id
}
