module "workload_demo" {
  source = "./vault-workload"

  count = var.demo_workload_enabled == true ? 1 : 0
  workload_name = "workload-demo"
}
