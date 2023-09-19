#custom policies
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

resource "aws_iam_policy" "harbor_policy" {
  name        = "${local.name}-harbor-policy"
  description = "Image registry (Harbor) policy for image replication"

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
resource "aws_iam_policy" "atlantis_policy" {
  name        = "${local.name}-atlantis-policy"
  description = "Atlantis IAM policy"
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
resource "aws_iam_policy" "vault_policy" {
  name        = "${local.name}-vault-policy"
  description = "Vault IAM policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "secretsmanager:*",
        "Effect" : "Allow",
        "Resource" : "arn:aws:secretsmanager:${var.region}:${local.aws_account}:*"
      }
    ]
  })

  tags = local.tags
}




