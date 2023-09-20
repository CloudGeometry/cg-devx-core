resource "vault_mount" "secret" {
  path        = "secret"
  type        = "kv-v2"
  description = "the vault kv v2 backend for core platform secrets"
}

resource "vault_mount" "users" {
  path        = "users"
  type        = "kv-v2"
  description = "kv v2 backend for users identities"
}

resource "vault_mount" "workloads" {
  path        = "workloads"
  type        = "kv-v2"
  description = "kv v2 backend for workloads secrets"
}
