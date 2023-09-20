module "workload_demo_template_repo" {
  source = "./repository"
  count = var.demo_workload_enabled == true ? 1 : 0

  repo_name          = "workload-demo-template"
  is_template        = true
}

module "workload_demo_repo" {
  source = "./repository"
  count = var.demo_workload_enabled == true ? 1 : 0

  repo_name          = "workload-demo"

}

module "workload_demo_iac_repo" {
  source = "./repository"
  count = var.demo_workload_enabled == true ? 1 : 0

  repo_name          = "workload-demo-iac"
  atlantis_enabled   = true
  atlantis_url       = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
}