terraform {

  required_providers {
    vault = {
      source = "hashicorp/vault"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
  }

}

locals {
  harbor_admin_user  = "admin"
  grafana_admin_user = "admin"
  atlantis_admin_user = "admin"
  sonarqube_admin_user = "admin"
}



