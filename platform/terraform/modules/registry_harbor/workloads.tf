module "workloads" {
  source   = "./project"
  for_each = var.workloads

  project_name = each.key
  description  = each.value.description
}