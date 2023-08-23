module "workload_template_repo" {
  source = "./repository"

  repo_name          = "workload-template"
  is_template        = true
}

module "workload1_repo" {
  source = "./repository"

  repo_name          = "workload1"

}

module "workload1_iac_repo" {
  source = "./repository"

  repo_name          = "workload1-iac"
  atlantis_enabled   = true
  atlantis_url       = var.atlantis_url
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
}