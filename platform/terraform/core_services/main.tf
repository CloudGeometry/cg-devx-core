terraform {
  # Remote backend configuration
  # <TF_REGISTRY_REMOTE_BACKEND>

  required_providers {
    harbor = {
      source = "goharbor/harbor"
    }
    sonarqube = {
      source = "jdamata/sonarqube"
    }
    restapi = {
      source = "Mastercard/restapi"
    }
  }
}

# Credential to harbor provider passed through env variables HARBOR_URL, HARBOR_USERNAME, and HARBOR_PASSWORD
provider "harbor" {
}

provider "sonarqube" {
  user = "admin"
  pass = var.code_quality_admin_password
  host = local.code_quality_url
}

provider "restapi" {
  uri = local.code_quality_url

  create_returns_object = false
  write_returns_object  = false
  username              = "admin"
  password              = var.code_quality_admin_password

  headers = {
    "Content-Type" = "application/x-www-form-urlencoded"
  }

}

locals {
  oidc_endpoint    = "https://<OIDC_PROVIDER_URL>"
  code_quality_url = "https://<CODE_QUALITY_INGRESS_URL>"
  workloads        = {
    # "workload-demo" = {
    # },
  }
}

module "registry" {
  source                       = "../modules/registry_harbor"
  workloads                    = local.workloads
  oidc_endpoint                = local.oidc_endpoint
  oidc_client_id               = var.registry_oidc_client_id
  oidc_client_secret           = var.registry_oidc_client_secret
  registry_main_robot_password = var.registry_main_robot_password
}

module "code_quality" {
  source                      = "../modules/code_quality_sonarqube"
  workloads                   = local.workloads
  oidc_endpoint               = local.oidc_endpoint
  code_quality_url            = local.code_quality_url
  oidc_client_id              = var.code_quality_oidc_client_id
  oidc_client_secret          = var.code_quality_oidc_client_secret
  code_quality_admin_password = var.code_quality_admin_password
}
