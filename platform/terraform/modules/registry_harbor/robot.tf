resource "harbor_robot_account" "main" {
  name        = "main-robot"
  description = "server level robot account"
  level       = "system"
  secret      = var.registry_main_robot_password
  #modify permissions to required later
  permissions {
    access {
      action   = "create"
      resource = "labels"
    }
    kind      = "system"
    namespace = "/"
  }
  permissions {
    access {
      action   = "pull"
      resource = "repository"
    }
    access {
      action   = "push"
      resource = "repository"
    }
    kind      = "project"
    namespace = "*"
  }
}
