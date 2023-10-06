resource "vault_policy" "admin" {
  name = "admin"

  policy = <<EOT
# Create and manage entities and groups
path "identity/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Configure the OIDC auth method
path "auth/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Write ACL policies
path "sys/policies/acl/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Allow default access to secret
path "secret/*" {
    capabilities = ["create", "read", "update", "delete", "list"]
}

# Allow full access to workloads secrets
path "workloads/*" {
    capabilities = ["create", "read", "update", "delete", "list"]
}

# allow admins to manage mounts
path "sys/mounts/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}

# List enabled secrets engine
path "sys/mounts" {
  capabilities = [ "read", "list" ]
}
  
# allow admins to manage auth methods
path "/sys/auth*" {
    capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# allow admins to manage auth methods
path "sys/auth/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}
EOT
}

resource "vault_policy" "developer" {
  name = "developer"

  policy = <<EOT
# Allow full write access to platform developers, without delete
path "secret/*" {
    capabilities = ["create", "read", "update", "list"]
}

# Allow write access to workloads secrets
path "workloads/*" {
    capabilities = ["create", "read", "update", "list"]
}

# List available secrets engines to retrieve accessor ID
path "sys/mounts" {
  capabilities = [ "read" ]
}
EOT
}
