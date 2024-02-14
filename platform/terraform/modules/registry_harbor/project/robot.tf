resource "random_password" "robot_password" {
  length  = 12
  special = false
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "harbor_robot_account" "workload_robot" {
  name        = "robot"
  description = "${var.project_name} workload project level robot account"
  level       = "project"
  secret      = resource.random_password.robot_password.result
  #need to define project robot permissions
  permissions {
    access {
      action   = "pull"
      resource = "repository"
    }
    kind      = "project"
    namespace = harbor_project.this.name
  }
}

resource "random_password" "push_robot_password" {
  length  = 12
  special = false
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "harbor_robot_account" "workload_push_robot" {
  name        = "push-robot"
  description = "${var.project_name} workload project level robot account with push permission"
  level       = "project"
  secret      = resource.random_password.push_robot_password.result
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
        resource = "scan"
      }
      access {
        action   = "create"
        effect   = "allow"
        resource = "artifact-label"
      }
      access {
        action   = "create"
        effect   = "allow"
        resource = "tag"
      }
      access {
        action   = "delete"
        effect   = "allow"
        resource = "tag"
      }
      access {
        action   = "list"
        resource = "tag"
      }
      access {
        action   = "list"
        effect   = "allow"
        resource = "artifact"
      }
      access {
        action   = "read"
        effect   = "allow"
        resource = "artifact"
      }
      access {
        action   = "stop"
        resource = "scan"
      }
      access {
        action   = "delete"
        effect   = "allow"
        resource = "artifact-label"
      }
      access {
        action   = "delete"
        effect   = "allow"
        resource = "artifact"
      }
    kind      = "project"
    namespace = harbor_project.this.name
  }
}
