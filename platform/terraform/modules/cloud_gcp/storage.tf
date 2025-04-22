resource "random_string" "uniq_bucket_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}

resource "google_storage_bucket" "artifacts_repository" {
  name     = "${local.name}-artifacts-repository-${random_string.uniq_bucket_suffix.result}"
  location = local.region

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  versioning {
    enabled = false
  }
  force_destroy = true
}

resource "google_storage_bucket" "backups_repository" {
  name     = "${local.name}-backups-repository-${random_string.uniq_bucket_suffix.result}"
  location = local.region

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  versioning {
    enabled = false
  }
  force_destroy = true
}