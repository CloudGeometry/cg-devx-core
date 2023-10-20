resource "harbor_config_auth" "oidc" {
  auth_mode          = "oidc_auth"
  primary_auth_mode  = true
  oidc_name          = "Vault OIDC Provider"
  oidc_endpoint      = "https://vault.cgdevx-demo.demoapps.click/v1/identity/oidc/provider/kubefirst"
  oidc_client_id     = "GA9g3lYNTbQEpbT5pSA7zcWX14JinLHK"
  oidc_client_secret = "hvo_secret_h5OqFQs5JLvrb19M86kMxruuz6koG95SmlD2xS0nXHX7SLM5ZPRUbG9Ga3VWlpMn"
  oidc_scope         = "openid,groups,user,profile,email"
  oidc_verify_cert   = true
  oidc_auto_onboard  = true
  oidc_user_claim    = "username"
  oidc_groups_claim  = "groups"
  oidc_admin_group   = "admins"
}
