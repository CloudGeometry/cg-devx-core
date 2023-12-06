terraform {
  required_providers {
    sonarqube = {
      source = "jdamata/sonarqube"
    }
  }
}

resource "sonarqube_project" "this" {
  name       = var.project_name
  project    = var.project_name
  visibility = "private"
}

resource "sonarqube_group" "workload_admins" {
  name        = "${var.project_name}-admins"
  description = "This is a ${var.project_name} admin group"
}

resource "sonarqube_group" "workload_developers" {
  name        = "${var.project_name}-developers"
  description = "This is a ${var.project_name} developers group"
}

resource "sonarqube_permissions" "workload-admins" {
  group_name  = "${var.project_name}-admins"
  project_key = sonarqube_project.this.project
  permissions = ["admin"]
  depends_on  = [sonarqube_group.workload_admins]
}

resource "sonarqube_permissions" "workload-developers" {
  group_name  = "${var.project_name}-developers"
  project_key = sonarqube_project.this.project
  permissions = ["codeviewer", "issueadmin", "securityhotspotadmin", "scan"]
  depends_on  = [sonarqube_group.workload_developers]
}
