resource "github_repository" "repo" {
  name        = var.repo_name
  description = var.description

  visibility             = var.visibility
  auto_init              = var.auto_init
  archive_on_destroy     = var.archive_on_destroy
  has_issues             = var.has_issues
  is_template            = var.is_template
  delete_branch_on_merge = var.delete_branch_on_merge

  dynamic "template" {
    for_each = length(var.template) != 0 ? [var.template] : []

    content {
      owner      = lookup(template.value, "owner", null)
      repository = lookup(template.value, "repository", null)
    }
  }

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
