output "admins_group_id" {
  value = vault_identity_group.admins.id
}

output "developers_group_id" {
  value = vault_identity_group.developers.id
}