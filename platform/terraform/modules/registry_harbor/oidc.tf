resource "harbor_config_auth" "oidc" {
  auth_mode          = "oidc_auth"
  primary_auth_mode  = true
  oidc_name          = "Vault OIDC Provider"
  oidc_endpoint      = var.oidc_endpoint
  oidc_client_id     = var.oidc_client_id
  oidc_client_secret = var.oidc_client_secret
  oidc_scope         = "openid,groups,user,profile,email"
  oidc_verify_cert   = true
  oidc_auto_onboard  = true
  oidc_user_claim    = "username"
  oidc_groups_claim  = "groups"
  oidc_admin_group   = "admins"
}
