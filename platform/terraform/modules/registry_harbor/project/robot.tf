resource "random_password" "robot_password" {
  length  = 12
  special = false
}

resource "harbor_robot_account" "workload_robot" {
  name        = "${var.project_name}-robot"
  description = "${var.project_name} workload project level robot account"
  level       = "project"
  secret      = resource.random_password.robot_password.result
#need to define project robot permissions
  permissions {
    access {
      action   = "pull"
      resource = "repository"
    }
    access {
      action   = "push"
      resource = "repository"
    }
    access {
      action   = "create"
      resource = "labels"
    }
    kind      = "project"
    namespace = harbor_project.this.name
  }
}

output "robot_user_pass" {
  value = resource.random_password.robot_password.result
  sensitive = true
}