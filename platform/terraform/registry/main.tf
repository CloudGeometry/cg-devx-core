terraform {
  # Remote backend configuration
  # <TF_ARTIFACT_REGISTRY_REMOTE_BACKEND>

  required_providers {
    harbor = {
      source = "goharbor/harbor"
    }
  }
}

# Credential to harbor provider passed through env variables HARBOR_URL, HARBOR_USERNAME, and HARBOR_PASSWORD
provider "harbor" {
  source = "goharbor/harbor"
}

locals {
  registry_oidc_endpoint = "https://<OIDC_PROVIDER_URL>"
  workloads = {
    # "workload-demo" = {
    # },
  }
  ### some harbor variables here
}

module "registry" {
  source                       = "../modules/registry_harbor"
  workloads                    = local.workloads
  oidc_endpoint                = local.registry_oidc_endpoint
  oidc_client_id               = var.registry_oidc_client_id
  oidc_client_secret           = var.registry_oidc_client_secret
  registry_main_robot_password = var.registry_main_robot_password
}
