resource "random_password" "main_robot_password" {
  length  = 12
  special = false
}

resource "harbor_robot_account" "main" {
  name        = "main-robot"
  description = "server level robot account"
  level       = "system"
  secret      = resource.random_password.main_robot_password.result
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
    access {
      action   = "read"
      resource = "helm-chart"
    }
    access {
      action   = "read"
      resource = "helm-chart-version"
    }
    kind      = "project"
    namespace = "*"
  }
}
