resource "random_password" "password" {
  length  = 12
  special = false
}

resource "harbor_robot_account" "project" {
  name        = "main-project"
  description = "project level robot account"
  level       = "project"
  secret      = resource.random_password.password.result
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
    namespace = harbor_project.main.name
  }
}
