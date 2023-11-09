module "vault_users" {
  for_each = var.users

  source = "./user"

  username             = each.key
  user_disabled        = each.value.user_disabled
  userpass_accessor    = data.vault_auth_backend.userpass.accessor
  github_username      = each.value.vcs_username
  email                = each.value.email
  first_name           = each.value.first_name
  last_name            = each.value.last_name
  github_team_slugs    = each.value.vcs_team_slugs
  acl_policies         = each.value.acl_policies
  oidc_groups_for_user = each.value.oidc_groups_for_user
}
