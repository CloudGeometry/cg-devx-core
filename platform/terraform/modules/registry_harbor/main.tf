terraform {
  required_providers {
    harbor = {
      source = "goharbor/harbor"
    }
  }
}

resource "harbor_config_system" "main" {
  project_creation_restriction = "adminonly"
  robot_token_expiration       = 365
  robot_name_prefix            = "robot@"
  storage_per_project          = 5
}