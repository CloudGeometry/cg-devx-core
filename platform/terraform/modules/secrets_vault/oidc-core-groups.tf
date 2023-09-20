resource "vault_identity_group" "developers" {
  name     = "developers"
  type     = "internal"
  policies = ["developer", "default"]

  # `resource "vault_identity_group_member_entity_ids"` manages this in the user module
  lifecycle {
    ignore_changes = [
      member_entity_ids
    ]
  }

  metadata = {
    version = "2"
  }
}

resource "vault_identity_group" "admins" {
  name     = "admins"
  type     = "internal"
  policies = ["admin", "default"]

  # `resource "vault_identity_group_member_entity_ids"` manages this in the user module
  lifecycle {
    ignore_changes = [
      member_entity_ids
    ]
  }

  metadata = {
    version = "2"
  }
}
