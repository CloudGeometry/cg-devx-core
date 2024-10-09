module "ci_sa" {
  source                      = "./modules/sa"
  service_account_name        = "${local.name}-ci-sa"
  display_name                = "argo-server"
  project                     = local.project_id
  kubernetes_service_accounts = concat([
    {
      namespace = "argo"
      name      = "argo-server"
    },
    {
      namespace = "argo"
      name      = "argo-workflow"
    }
  ], local.ci_sa_workloads)
  roles = ["roles/storage.objectAdmin"]
}

module "cert_manager_sa" {
  source                      = "./modules/sa"
  service_account_name        = "${local.name}-cert-manager"
  display_name                = "cert-manager"
  project                     = local.project_id
  kubernetes_service_accounts = [
    {
      namespace = "cert-manager"
      name      = "cert-manager"
    }
  ]
  roles = ["roles/dns.admin"]
}

module "external_dns_sa" {
  source                      = "./modules/sa"
  service_account_name        = "${local.name}-external-dns"
  display_name                = "external-dns"
  project                     = local.project_id
  kubernetes_service_accounts = [
    {
      namespace = "external-dns"
      name      = "external-dns"
    }
  ]
  roles = ["roles/dns.admin"]
}

module "secret_manager_sa" {
  source                      = "./modules/sa"
  service_account_name        = "${local.name}-vault"
  display_name                = "vault"
  project                     = local.project_id
  kubernetes_service_accounts = [
    {
      namespace = "vault"
      name      = "vault"
    }
  ]
  roles = [
    "roles/cloudkms.viewer", "roles/cloudkms.cryptoKeyEncrypterDecrypter",
    "roles/cloudkms.publicKeyViewer", "roles/resourcemanager.tagViewer"
  ]
}

module "iac_pr_automation_sa" {
  source                      = "./modules/sa"
  service_account_name        = "${local.name}-atlantis"
  display_name                = "atlantis"
  project                     = local.project_id
  kubernetes_service_accounts = [
    {
      namespace = "atlantis"
      name      = "atlantis"
    }
  ]
  roles = ["roles/editor", "roles/iam.securityAdmin"]
}
