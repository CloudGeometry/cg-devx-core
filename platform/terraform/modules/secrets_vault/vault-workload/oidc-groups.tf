resource "vault_identity_group" "admins" {
  name     = "${var.workload_name}-admins"
  type     = "internal"
  policies = ["${var.workload_name}-admin", "default"]

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

resource "vault_identity_group" "developers" {
  name     = "${var.workload_name}-developers"
  type     = "internal"
  policies = ["${var.workload_name}-developer", "default"]

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