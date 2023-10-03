#custom policies
resource "aws_iam_policy" "argocd" {
  name        = "${local.name}-argocd-policy"
  description = "ArgoCD IAM policy"

  policy = jsonencode({
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

resource "aws_iam_policy" "argoworkflow" {
  name        = "${local.name}-argoworkflow-policy"
  description = "ArgoWorkFlow IAM policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "s3:*",
        "Effect" : "Allow",
        "Resource" : "arn:aws:s3:::*"
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_policy" "registry_policy" {
  name        = "${local.name}-registry-policy"
  description = "Image registry policy for image replication"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "ecr:ReplicateImage"
        ],
        "Effect" : "Allow",
        "Resource" : "arn:aws:ecr:${var.region}:${local.aws_account}:*"
      }
    ]
  })
  tags = local.tags
}
resource "aws_iam_policy" "iac_pr_automation_policy" {
  name        = "${local.name}-iac-pr-automation-policy"
  description = "Atlantis IAM policy"
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




