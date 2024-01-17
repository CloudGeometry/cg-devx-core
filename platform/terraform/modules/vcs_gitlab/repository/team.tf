data "gitlab_current_user" "current_user" {}

resource "gitlab_group" "owners" {
  name             = "${var.repo_name}-owners"
  description      = "owners of the ${var.repo_name}"
  parent_id        = var.vcs_owner
  path             = "${var.repo_name}-owners"
  visibility_level = "private"
}
resource "gitlab_group" "developers" {
  name             = "${var.repo_name}-developers"
  description      = "developers of the ${var.repo_name}"
  parent_id        = var.vcs_owner
  path             = "${var.repo_name}-developers"
  visibility_level = "private"
}

resource "gitlab_group" "maintainers" {
  name             = "${var.repo_name}-maintainers"
  description      = "maintainers of the ${var.repo_name}"
  parent_id        = var.vcs_owner
  path             = "${var.repo_name}-maintainers"
  visibility_level = "private"
}

resource "gitlab_group" "reporters" {
  name             = "${var.repo_name}-reporters"
  description      = "reporters of the ${var.repo_name}"
  parent_id        = var.vcs_owner
  path             = "${var.repo_name}-reporters"
  visibility_level = "private"
}

resource "gitlab_group" "guests" {
  name             = "${var.repo_name}-guests"
  description      = "Guests of the ${var.repo_name}"
  parent_id        = var.vcs_owner
  path             = "${var.repo_name}-guests"
  visibility_level = "private"
}

resource "gitlab_project_share_group" "maintainers_project" {
  project      = gitlab_project.repo.id
  group_id     = gitlab_group.maintainers.id
  group_access = "maintainer"
}

resource "gitlab_project_share_group" "developers_project" {
  project      = gitlab_project.repo.id
  group_id     = gitlab_group.developers.id
  group_access = "developer"
}

resource "gitlab_project_share_group" "reporters_project" {
  project      = gitlab_project.repo.id
  group_id     = gitlab_group.reporters.id
  group_access = "reporter"
}

resource "gitlab_project_share_group" "guests_project" {
  project      = gitlab_project.repo.id
  group_id     = gitlab_group.guests.id
  group_access = "guest"
}
