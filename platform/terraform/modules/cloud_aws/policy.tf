#custom policies

resource "aws_iam_policy" "ci" {
  name        = "${local.name}-ci-policy"
  description = "Cloud Native CI IAM policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "s3:*",
        "Effect" : "Allow",
        "Resource" : module.artifacts_repository.s3_bucket_arn
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_policy" "iac_pr_automation_policy" {
  name        = "${local.name}-iac-pr-automation-policy"
  description = "IaC PR Automation tool IAM policy"
  policy      = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "eks:*",
        "Effect" : "Allow",
        "Resource" : "arn:aws:eks:${var.region}:${local.aws_account}:*"
      }
    ]
  })

  tags = local.tags
}
resource "aws_iam_policy" "secret_manager_policy" {
  name        = "${local.name}-secret-manager-policy"
  description = "Secret manager IAM policy"
  policy      = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "kms:GetPublicKey",
          "kms:GetKeyRotationStatus",
          "kms:GetKeyPolicy",
          "kms:DescribeKey",
          "kms:ListKeyPolicies",
          "kms:ListResourceTags",
          "tag:GetResources",
          "kms:Encrypt",
          "kms:Decrypt"
        ],
        "Effect" : "Allow",
        "Resource" : "arn:aws:kms:${var.region}:${local.aws_account}:key/*"
      }
    ]
  })

  tags = local.tags
}




