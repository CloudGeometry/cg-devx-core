resource "github_team" "admins" {
  name        = "${var.repo_name}-admins"
  description = "administrators of the ${var.repo_name}"
  privacy     = "closed"
}

resource "github_team" "maintainers" {
  name        = "${var.repo_name}-maintainers"
  description = "maintainers using the ${var.repo_name}"
  privacy     = "closed"
}

resource "github_team" "writers" {
  name        = "${var.repo_name}-writers"
  description = "writers using the ${var.repo_name}"
  privacy     = "closed"
}

resource "github_team" "readers" {
  name        = "${var.repo_name}-readers"
  description = "readers using the ${var.repo_name}"
  privacy     = "closed"
}

resource "github_team_repository" "team_admins" {
  team_id    = github_team.admins.id
  repository = github_repository.repo.name
  permission = "admin"
}

resource "github_team_repository" "team_maintainers" {
  team_id    = github_team.maintainers.id
  repository = github_repository.repo.name
  permission = "maintain"
}

resource "github_team_repository" "team_writers" {
  team_id    = github_team.writers.id
  repository = github_repository.repo.name
  permission = "push"
}

resource "github_team_repository" "team_readers" {
  team_id    = github_team.readers.id
  repository = github_repository.repo.name
  permission = "pull"
}