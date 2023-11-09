terraform {
  required_providers {
    sonarqube = {
      source = "jdamata/sonarqube"
    }
    restapi = {
      source = "Mastercard/restapi"
    }
  }
}

resource "sonarqube_project" "main" {
  name       = "main"
  project    = "main"
  visibility = "private"
}

resource "sonarqube_setting" "server_base_url" {
  key   = "sonar.core.serverBaseURL"
  value = var.code_quality_url
}