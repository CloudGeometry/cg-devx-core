resource "vault_generic_secret" "docker_config" {
  path = "secret/dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "ghcr.io" : { "auth" : "${var.b64_docker_auth}" } } }),
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "registry_auth" {
  path = "secret/registry-auth"

  data_json = jsonencode(
    {
      auth = jsonencode({ "auths" : { "ghcr.io" : { "auth" : "${var.b64_docker_auth}" } } }),
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "ci_secrets" {
  path = "secret/ci-secrets"

  data_json = jsonencode(
    {
      SSH_PRIVATE_KEY       = var.cgdevxbot_ssh_private_key,
      PERSONAL_ACCESS_TOKEN = var.<GIT_PROVIDER>_token,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "vault_generic_secret" "atlantis_secrets" {
  path = "secret/atlantis"

  # variables that appear duplicated are for circumstances where both terraform
  # and seperately the terraform provider each need the value

  data_json = jsonencode(
    {
      ARGO_SERVER_URL                     = "argo.argo.svc.cluster.local:2746",
      # github specific section
      # ----
      ATLANTIS_GH_HOSTNAME                = "github.com",
      ATLANTIS_GH_TOKEN                   = var.<GIT_PROVIDER>_token,
      ATLANTIS_GH_USER                    = "<GIT_USER_NAME>",
      ATLANTIS_GH_WEBHOOK_SECRET          = var.atlantis_repo_webhook_secret,
      GITHUB_OWNER                        = "<GIT_ORGANIZATION_NAME>",
      GITHUB_TOKEN                        = var.<GIT_PROVIDER>_token,
      # ----
      TF_VAR_atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret,
      TF_VAR_atlantis_repo_webhook_url    = var.atlantis_repo_webhook_url,
      TF_VAR_b64_docker_auth              = var.b64_docker_auth,
      TF_VAR_<GIT_PROVIDER>_token         = var.<GIT_PROVIDER>_token,
      # aws specific section
      # ----
      TF_VAR_aws_account_id               = "<CLOUD_ACCOUNT>",
      TF_VAR_aws_region                   = "<CLOUD_REGION>",
      # ----
      TF_VAR_hosted_zone_name             = "<DOMAIN_NAME>",
      TF_VAR_cgdevxbot_ssh_public_key     = var.cgdevxbot_ssh_public_key,
      TF_VAR_cgdevxbot_ssh_private_key    = var.cgdevxbot_ssh_private_key,
      TF_VAR_vault_addr                   = "http://vault.vault.svc.cluster.local:8200",
      TF_VAR_vault_token                  = var.vault_token,
      VAULT_ADDR                          = "http://vault.vault.svc.cluster.local:8200",
      VAULT_TOKEN                         = var.vault_token,
    }
  )

  depends_on = [vault_mount.secret]
}

resource "random_password" "grafana_password" {
  length           = 22
  special          = true
  override_special = "!#$"
}

resource "vault_generic_secret" "grafana_secrets" {
  path = "secret/grafana-secrets"

  data_json = jsonencode(
    {
      GRAFANA_USER       = "admin",
      GRAFANA_PASS       = random_password.grafana_password.result,
    }
  )

  depends_on = [vault_mount.secret]
}