locals {
  b64_docker_auth      = base64encode("robot@main-robot:${random_password.harbor_main_robot_password.result}")
  harbor_admin_user    = "admin"
  grafana_admin_user   = "admin"
  atlantis_admin_user  = "admin"
  sonarqube_admin_user = "admin"
}

resource "vault_generic_secret" "docker_config" {
  path = "secret/dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.b64_docker_auth}" } } }),
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "registry_auth" {
  path = "secret/registry-auth"

  data_json = jsonencode(
    {
      auth = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.b64_docker_auth}" } } }),
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "ci_secrets" {
  path = "secret/ci-secrets"

  data_json = jsonencode(
    {
      SSH_PRIVATE_KEY       = var.vcs_bot_ssh_private_key,
      PERSONAL_ACCESS_TOKEN = var.vcs_token,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "atlantis_secrets" {
  path = "secret/atlantis/envs-secrets"

  # variables that appear duplicated are for circumstances where both terraform
  # and separately the terraform provider each need the value

  data_json = jsonencode(
    {
      ARGO_SERVER_URL                     = "argo.argo.svc.cluster.local:2746",
      # github specific section
      ATLANTIS_GH_HOSTNAME                = "github.com",
      ATLANTIS_GH_TOKEN                   = var.vcs_token,
      ATLANTIS_GH_USER                    = "<GIT_USER_LOGIN>",
      ATLANTIS_GH_WEBHOOK_SECRET          = var.atlantis_repo_webhook_secret,
      GITHUB_OWNER                        = "<GIT_ORGANIZATION_NAME>",
      GITHUB_TOKEN                        = var.vcs_token,
      # ----
      TF_VAR_atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret,
      TF_VAR_atlantis_repo_webhook_url    = var.atlantis_repo_webhook_url,
      TF_VAR_vcs_token                    = var.vcs_token,
      TF_VAR_cluster_endpoint             = var.cluster_endpoint
      # ----
      TF_VAR_hosted_zone_name             = "<DOMAIN_NAME>",
      TF_VAR_vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key,
      TF_VAR_vcs_bot_ssh_private_key      = var.vcs_bot_ssh_private_key,
      # harbor specific section
      TF_VAR_registry_oidc_client_id      = module.harbor.vault_oidc_client_id,
      TF_VAR_registry_oidc_client_secret  = module.harbor.vault_oidc_client_secret,
      TF_VAR_registry_main_robot_password = random_password.harbor_main_robot_password.result,
      HARBOR_URL                          = "https://<REGISTRY_INGRESS_URL>",
      HARBOR_USERNAME                     = local.harbor_admin_user,
      HARBOR_PASSWORD                     = random_password.harbor_password.result,
      # ----

      # vault specific section
      TF_VAR_vault_addr                      = "http://vault.vault.svc.cluster.local:8200",
      TF_VAR_vault_token                     = var.vault_token,
      VAULT_ADDR                             = "http://vault.vault.svc.cluster.local:8200",
      VAULT_TOKEN                            = var.vault_token,
      # code quality specific section
      TF_VAR_code_quality_oidc_client_id     = module.harbor.vault_oidc_client_id,
      TF_VAR_code_quality_oidc_client_secret = module.harbor.vault_oidc_client_secret,
      TF_VAR_code_quality_admin_password     = random_password.sonarqube_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "random_password" "grafana_password" {
  length           = 22
  special          = true
  override_special = "!#$"
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "vault_generic_secret" "grafana_secrets" {
  path = "secret/grafana-secrets"

  data_json = jsonencode(
    {
      GRAFANA_USER = local.grafana_admin_user,
      GRAFANA_PASS = random_password.grafana_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}

# atlantis web ui basic auth credentials
resource "random_password" "atlantis_password" {
  length           = 22
  special          = true
  override_special = "!#$"
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "vault_generic_secret" "atlantis_auth_secrets" {
  path = "secret/atlantis/basic-auth-secrets"

  data_json = jsonencode(
    {
      username = local.atlantis_admin_user,
      password = random_password.atlantis_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}

# harbor web ui admin auth credentials
resource "random_password" "harbor_password" {
  length  = 22
  special = false
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "vault_generic_secret" "harbor_admin_secret" {
  path = "secret/harbor/admin-auth"

  data_json = jsonencode(
    {
      HARBOR_ADMIN_NAME     = local.harbor_admin_user,
      HARBOR_ADMIN_PASSWORD = random_password.harbor_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "random_password" "harbor_main_robot_password" {
  length  = 22
  special = false
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "vault_generic_secret" "harbor_main_robot_secret" {
  path = "secret/harbor/main-robot-auth"

  data_json = jsonencode(
    {
      HARBOR_ROBOT_NAME     = "robot@main-robot",
      HARBOR_ROBOT_PASSWORD = random_password.harbor_main_robot_password.result,
      HARBOR_ROBOT_B64_AUTH = local.b64_docker_auth,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "random_password" "sonarqube_password" {
  length  = 22
  special = false
  min_lower = 1
  min_upper = 1
  min_numeric = 1
}

resource "vault_generic_secret" "sonarqube_admin_secret" {
  path = "secret/sonarqube/admin-auth"

  data_json = jsonencode(
    {
      username        = local.sonarqube_admin_user,
      currentPassword = "admin",
      password        = random_password.sonarqube_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}
