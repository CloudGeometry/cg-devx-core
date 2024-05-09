data "vault_auth_backend" "userpass" {
  path = "userpass"
}

data "vault_identity_group" "oidc_identity_groups" {
  for_each   = local.group_map
  group_name = "${each.key}"
}
