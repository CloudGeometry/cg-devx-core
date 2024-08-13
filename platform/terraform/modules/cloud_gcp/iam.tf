module "ci_sa" {
  source                          = "./modules/sa"
  service_account_name            = "${local.name}-ci-sa"
  kubernetes_service_account_name = "argo-server"
  display_name                    = "argo-workflow"
  project                         = local.project_id
  service_account_namespace       = "argo-server"
  roles                            = ["roles/storage.objectAdmin"]
}

module "cert_manager_sa" {
  source                          = "./modules/sa"
  service_account_name            = "${local.name}-cert-manager"
  kubernetes_service_account_name = "cert-manager"
  display_name                    = "cert-manager"
  project                         = local.project_id
  service_account_namespace       = "cert-manager"
  roles                            = ["roles/dns.admin"]
}

module "external_dns_sa" {
  source                          = "./modules/sa"
  service_account_name            = "${local.name}-external-dns"
  kubernetes_service_account_name = "external-dns"
  display_name                    = "external-dns"
  project                         = local.project_id
  service_account_namespace       = "external-dns"
  roles                            = ["roles/dns.admin"]
}

module "secret_manager_sa" {
  source                          = "./modules/sa"
  service_account_name            = "${local.name}-vault"
  kubernetes_service_account_name = "vault"
  display_name                    = "vault"
  project                         = local.project_id
  service_account_namespace       = "vault"
  roles                           = ["roles/cloudkms.viewer", "roles/cloudkms.cryptoKeyEncrypterDecrypter", "roles/cloudkms.publicKeyViewer", "roles/resourcemanager.tagViewer"]
}

module "iac_pr_automation_sa" {
  source                          = "./modules/sa"
  service_account_name            = "${local.name}-atlantis"
  kubernetes_service_account_name = "atlantis"
  display_name                    = "atlantis"
  project                         = local.project_id
  service_account_namespace       = "atlantis"
  roles                            = ["roles/editor", "roles/iam.securityAdmin"]
}