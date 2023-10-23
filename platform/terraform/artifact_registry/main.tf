terraform {
  # Remote backend configuration
  # <TF_ARTIFACT_REGISTRY_REMOTE_BACKEND>
}

# Credential to harbor provider passed through env variables HARBOR_URL, HARBOR_USERNAME, and HARBOR_PASSWORD
provider "harbor" {
}

locals {
  artifact_registry_oidc_endpoint = "https://<OIDC_PROVIDER_URL>"
  workloads        = {
    "workload-demo" = {
    },
  }
### some harbor variables here
}

module "artifact_registry" {
  source      = "../modules/artifact_registry_harbor"
  workloads          = local.workloads
  oidc_endpoint      = local.artifact_registry_oidc_endpoint
  oidc_client_id     = var.artifact_registry_oidc_client_id
  oidc_client_secret = var.artifact_registry_oidc_client_secret
}