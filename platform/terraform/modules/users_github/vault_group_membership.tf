locals {
  group_map = {
    for groupname, users in transpose({
      for username, user in var.users : username =>lookup(user, "oidc_groups_for_user", [])
    }) : groupname => [for u in users : module.vault_users[u].vault_identity_entity_id]
  }
}

resource "vault_identity_group_member_entity_ids" "oidc_group_membership" {
  for_each = local.group_map

  group_id = data.vault_identity_group.oidc_identity_groups[each.key].group_id
  member_entity_ids = each.value
}

