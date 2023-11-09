resource "vault_identity_entity" "user" {
  name     = var.username
  disabled = var.user_disabled
  metadata = {
    email      = var.email
    first_name = var.first_name
    last_name  = var.last_name
  }
}

resource "vault_identity_entity_alias" "user" {
  name           = var.username
  mount_accessor = var.userpass_accessor
  canonical_id   = vault_identity_entity.user.id
}

resource "random_password" "password" {
  length           = 25
  special          = true
  override_special = "!#$@"
}

resource "vault_generic_endpoint" "user" {
  path                 = "auth/userpass/users/${var.username}"
  ignore_absent_fields = true
  disable_read         = true # check is it necessary

  data_json = jsonencode(
    {
      policies  = var.acl_policies,
      password  = random_password.password.result
      token_ttl = "1h"
    }
  )
}

resource "vault_generic_secret" "user" {
  path = "users/${var.username}"

  data_json = <<EOT
{
  "initial-password": "${random_password.password.result}"
}
EOT
}

resource "github_team_membership" "team_membership" {
  for_each = toset(var.github_team_slugs)

  team_id  = each.value
  username = var.github_username
  role     = "member"
}
