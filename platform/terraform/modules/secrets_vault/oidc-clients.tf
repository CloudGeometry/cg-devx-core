module "argo" {
  source = "./oidc-client"

  depends_on = [
    vault_identity_oidc_provider.cgdevx
  ]

  app_name               = "argo"
  identity_group_ids     = [vault_identity_group.admins.id, vault_identity_group.developers.id]
  oidc_provider_key_name = vault_identity_oidc_key.key.name
  redirect_uris = [
    "https://<ARGO_WORKFLOWS_INGRESS_URL>/oauth2/callback",
  ]
  secret_mount_path = "secret"
}

module "argocd" {
  source = "./oidc-client"

  depends_on = [
    vault_identity_oidc_provider.cgdevx
  ]

  app_name               = "argocd"
  identity_group_ids     = [vault_identity_group.admins.id, vault_identity_group.developers.id]
  oidc_provider_key_name = vault_identity_oidc_key.key.name
  redirect_uris = [
    "https://<ARGOCD_INGRESS_URL>/auth/callback",
  ]
  secret_mount_path = "secret"
}

module "grafana" {
  source = "./oidc-client"

  depends_on = [
    vault_identity_oidc_provider.cgdevx
  ]

  app_name               = "grafana"
  identity_group_ids     = [vault_identity_group.admins.id, vault_identity_group.developers.id]
  oidc_provider_key_name = vault_identity_oidc_key.key.name
  redirect_uris = [
    "https://<GRAFANA_INGRESS_URL>/login/generic_oauth",
  ]
  secret_mount_path = "secret"
}

module "harbor" {
  source = "./oidc-client"

  depends_on = [
    vault_identity_oidc_provider.cgdevx
  ]

  app_name               = "harbor"
  identity_group_ids     = [vault_identity_group.admins.id, vault_identity_group.developers.id]
  oidc_provider_key_name = vault_identity_oidc_key.key.name
  redirect_uris = [
    "https://<HARBOR_INGRESS_URL>/c/oidc/callback",
  ]
  secret_mount_path = "secret"
}

module "sonarqube" {
  source = "./oidc-client"

  depends_on = [
    vault_identity_oidc_provider.cgdevx
  ]

  app_name               = "sonarqube"
  identity_group_ids     = [vault_identity_group.admins.id, vault_identity_group.developers.id]
  oidc_provider_key_name = vault_identity_oidc_key.key.name
  redirect_uris = [
    "https://<SONARQUBE_INGRESS_URL>/oauth2/callback/oidc",
  ]
  secret_mount_path = "secret"
}