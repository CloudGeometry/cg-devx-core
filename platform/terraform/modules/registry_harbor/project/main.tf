terraform {
  required_providers {
    harbor = {
      source = "goharbor/harbor"
    }
  }
}

resource "harbor_project" "this" {
  name   = var.project_name
  public = false
}

resource "harbor_immutable_tag_rule" "this" {
  project_id    = harbor_project.this.id
  repo_matching = "**"
  tag_matching  = "**"
}

resource "harbor_group" "workload_developers" {
  group_name = "${var.project_name}-developers"
  group_type = 3
}

resource "harbor_group" "workload_admins" {
  group_name = "${var.project_name}-admins"
  group_type = 3
}

resource "harbor_project_member_group" "platform_developers" {
  project_id = harbor_project.this.id
  group_name = "developers"
  role       = "guest"
  type       = "oidc"
}

resource "harbor_project_member_group" "workload_developers" {
  project_id = harbor_project.this.id
  group_name = "${var.project_name}-developers"
  ##choose correct role for workload developers from projectadmin, maintainer(master), developer, guest, limited guest
  ## https://goharbor.io/docs/2.0.0/administration/managing-users/user-permissions-by-role/
  role       = "developer"
  type       = "oidc"
}

resource "harbor_project_member_group" "workload_admins" {
  project_id = harbor_project.this.id
  group_name = "${var.project_name}-admins"
  role       = "maintainer"
  type       = "oidc"
}