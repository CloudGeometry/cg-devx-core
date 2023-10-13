terraform {

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.17.0"
    }
    vault = {
      source = "hashicorp/vault"
    }
  }
}

data "vault_auth_backend" "userpass" {
  path = "userpass"
}

data "vault_identity_group" "admins" {
  group_name = "admins"
}

data "vault_identity_group" "developers" {
  group_name = "developers"
}

resource "vault_identity_group_member_entity_ids" "admins_membership" {
  member_entity_ids = [module.cgdevx-bot.vault_identity_entity_id]
  group_id = data.vault_identity_group.admins.group_id
}

# resource "vault_identity_group_member_entity_ids" "developers_membership" {
#   member_entity_ids = module.developers.vault_identity_entity_ids
#   group_id = data.vault_identity_group.developers.group_id
# }

# output "vault_identity_entity_ids" {
#   value = [
#     module.cgdevx-bot.vault_identity_entity_id,
#     module.cgdevx-bot2.vault_identity_entity_id,
#     module.cgdevx-bot3.vault_identity_entity_id,
#   ]
# }