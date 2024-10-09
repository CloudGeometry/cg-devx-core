# Create Service Account
resource "google_service_account" "this" {
  account_id   = var.service_account_name
  display_name = var.display_name
  project      = var.project
}

# Bind Service Account to multiple Kubernetes Service Accounts
resource "google_service_account_iam_member" "k8s_bindings" {
  for_each = { for ksa in var.kubernetes_service_accounts : "${ksa.namespace}-${ksa.name}" => ksa }

  service_account_id = google_service_account.this.name
  role               = data.google_iam_role.workload_identity_user.name

  member = "serviceAccount:${var.project}.svc.id.goog[${each.value.namespace}/${each.value.name}]"
}

# Role Memberships
# Loop over the roles list and create a separate IAM member for each role
resource "google_project_iam_member" "roles" {
  for_each = toset(var.roles)

  member  = "serviceAccount:${google_service_account.this.email}"
  project = var.project
  role    = each.key
}

# Key
resource "google_service_account_key" "this" {
  count = var.create_service_account_key ? 1 : 0

  service_account_id = google_service_account.this.name
}

# Bind Service Account to Key Ring
resource "google_kms_key_ring_iam_member" "this-crypto_key_encrypter_decrypter" {
  count = var.create_service_account_key ? 1 : 0

  key_ring_id = var.keyring
  role        = data.google_iam_role.crypto_key_encrypter_decrypter.name

  member = "serviceAccount:${google_service_account.this.email}"
}

# Bind Service Account to Key Ring
resource "google_kms_key_ring_iam_member" "this" {
  count = var.create_service_account_key ? 1 : 0

  key_ring_id = var.keyring
  role        = data.google_iam_role.admin.name

  member = "serviceAccount:${google_service_account.this.email}"
}

# Permissions for Bucket
resource "google_storage_bucket_iam_member" "this" {
  count = var.create_bucket_iam_access ? 1 : 0

  bucket = var.bucket_name
  role   = data.google_iam_role.storage_objectadmin.name
  member = "serviceAccount:${google_service_account.this.email}"
}
