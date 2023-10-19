data "vault_auth_backend" "userpass" {
  path = "userpass"
}

data "vault_identity_group" "oidc_identity_groups" {
  for_each = var.oidc_groups
  group_name      = "${each.key}"
}
