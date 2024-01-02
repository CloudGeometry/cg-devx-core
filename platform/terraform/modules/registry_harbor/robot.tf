resource "harbor_robot_account" "main" {
  name        = "main-robot"
  description = "server level robot account"
  level       = "system"
  secret      = var.registry_main_robot_password
  #modify permissions to required later

  permissions {
    kind      = "project"
    namespace = "*"

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
        action   = "list"
        effect   = "allow"
        resource = "repository"
      }
      access {
        action   = "pull"
        effect   = "allow"
        resource = "repository"
      }
      access {
        action   = "push"
        effect   = "allow"
        resource = "repository"
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
        resource = "repository"
      }
      access {
        action   = "delete"
        effect   = "allow"
        resource = "artifact"
      }
    }
}