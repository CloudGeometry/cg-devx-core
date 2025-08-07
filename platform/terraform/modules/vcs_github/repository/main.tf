resource "github_repository" "repo" {
  name        = var.repo_name
  description = var.description

  visibility             = var.visibility
  auto_init              = var.auto_init
  archive_on_destroy     = var.archive_on_destroy
  has_issues             = var.has_issues
  delete_branch_on_merge = var.delete_branch_on_merge
  allow_merge_commit     = var.allow_merge_commit
  # atlantis currently doesn't support branch protection with required linear historyw when repo settings allowed merge commits
  # need to monitor these issues
  # https://github.com/runatlantis/atlantis/issues/1176
  # https://github.com/runatlantis/atlantis/pull/3211
  # https://github.com/runatlantis/atlantis/pull/3276
  # https://github.com/runatlantis/atlantis/pull/3321


  dynamic "template" {
    for_each = length(var.template) != 0 ? [var.template] : []

    content {
      owner      = lookup(template.value, "owner", null)
      repository = lookup(template.value, "repository", null)
    }
  }

}

# Protect the main branch of the repository. Additionally, require
# only allow the engineers team merge to the branch.

resource "github_branch_protection" "this" {
  count         = var.branch_protection && var.vcs_subscription_plan ? 1 : 0
  repository_id = github_repository.repo.node_id

  pattern                         = var.default_branch_name
  enforce_admins                  = true
  allows_deletions                = false
  allows_force_pushes             = false
  required_linear_history         = true
  require_conversation_resolution = true

  # required_status_checks {
  #   strict   = false
  # }

  # required_pull_request_reviews {
  #   dismiss_stale_reviews  = true
  #   restrict_dismissals    = true
  #   dismissal_restrictions = [
  #     data.github_user.example.node_id,
  #     github_team.example.node_id,
  #     "/exampleuser",
  #     "exampleorganization/exampleteam",
  #   ]
  # }

  # push_restrictions = [
  #   data.github_user.example.node_id,
  #   "/exampleuser",
  #   "exampleorganization/exampleteam",
  #   # you can have more than one type of restriction (teams + users). If you use
  #   # more than one type, you must use node_ids of each user and each team.
  #   # github_team.example.node_id
  #   # github_user.example-2.node_id
  # ]

  # force_push_bypassers = [
  #   data.github_user.example.node_id,
  #   "/exampleuser",
  #   "exampleorganization/exampleteam",
  #   # you can have more than one type of restriction (teams + users)
  #   # github_team.example.node_id
  #   # github_team.example-2.node_id
  # ]
}


output "repo_name" {
  value = github_repository.repo.name
}

output "repo_git_clone_url" {
  value = github_repository.repo.git_clone_url
}

output "repo_git_html_url" {
  value = github_repository.repo.html_url
}

output "repo_git_ssh_clone_url" {
  value = github_repository.repo.ssh_clone_url
}

output "repo_id" {
  value = github_repository.repo.repo_id
}
