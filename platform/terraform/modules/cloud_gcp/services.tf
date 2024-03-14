# Enables Cloud Key Management Service (KMS)
resource "google_project_service" "kms_service" {
  project = local.project_id
  service = "cloudkms.googleapis.com"
  disable_on_destroy = false
}

# Enables Cloud Resource Manager
resource "google_project_service" "resource_manager_service" {
  project = local.project_id
  service = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# Enables Compute Engine
resource "google_project_service" "compute_engine_service" {
  project = local.project_id
  service = "compute.googleapis.com"
  disable_on_destroy = false
}

# Enables Identity and Access Management (IAM)
resource "google_project_service" "iam_service" {
  project = local.project_id
  service = "iam.googleapis.com"
  disable_on_destroy = false
}

# Enables IAM Service Account Credentials API
resource "google_project_service" "iam_credentials_service" {
  project = local.project_id
  service = "iamcredentials.googleapis.com"
  disable_on_destroy = false
}

# Enables Kubernetes Engine
resource "google_project_service" "kubernetes_engine_service" {
  project = local.project_id
  service = "container.googleapis.com"
  disable_on_destroy = false
}
