module "workloads" {
  source   = "./vault-workload"
  for_each = var.workloads

  workload_name = each.key
  description   = each.value.description
}
