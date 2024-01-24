resource "vault_policy" "workload-admin" {
  name = "${var.workload_name}-admin"

  policy = <<EOT
# Allow full access to workloads secrets
path "workloads/+/${var.workload_name}/*" {
    capabilities = ["create", "read", "update", "delete", "list"]
}
# Allow list for workloads path
path "workloads/+/" {
    capabilities = ["list"]
}
# List available secrets engines to retrieve accessor ID
path "sys/mounts" {
  capabilities = [ "read" ]
}
EOT
}

resource "vault_policy" "workload-developer" {
  name = "${var.workload_name}-developer"

  policy = <<EOT
# Allow write access to workloads secrets
path "workloads/+/${var.workload_name}/*" {
    capabilities = ["create", "read", "update", "list"]
}
# Allow list for workloads path
path "workloads/+/" {
    capabilities = ["list"]
}
# List available secrets engines to retrieve accessor ID
path "sys/mounts" {
  capabilities = [ "read" ]
}
EOT
}
