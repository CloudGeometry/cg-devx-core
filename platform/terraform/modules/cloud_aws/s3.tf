# random suffix for artifacts s3 bucket
resource "random_string" "random_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}

module "artifacts_repository" {
  source = "terraform-aws-modules/s3-bucket/aws"
  version = "4.11.0"

  bucket = "${local.name}-artifacts-repository-${random_string.random_suffix.id}"
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  force_destroy  = true
  lifecycle_rule = [
    {
      id     = "delete-after-30-days"
      status = "Enabled"

      expiration = {
        days = 30
      }
      # transition example
      # transition = {
      #   days = 30
      #   storage_class = "GLACIER"
      # }
    }
  ]
}

module "backups_repository" {
  source = "terraform-aws-modules/s3-bucket/aws"
  version = "4.11.0"

  bucket = "${local.name}-backups-repository-${random_string.random_suffix.id}"
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  force_destroy  = true
  lifecycle_rule = [
    {
      id     = "delete-after-90-days"
      status = "Enabled"

      expiration = {
        days = 90
      }
    }
  ]
}