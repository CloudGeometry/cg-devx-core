
################################################################################
# Supporting IAM role and policy Resources
################################################################################

module "sample_role" {
  source  = "terraform-aws-modules/iam/aws/modules/iam-role-for-service-accounts-eks"
  version = "5.20.0"

  tags = local.tags
}

resource "aws_iam_policy" "sample_policy" {

  policy = <<EOT
EOT
}


#Need create roles and policies for
# CNI
# CSI
# argo workflow
# atlantis
# cert manager
# container registry
# external DNS
# vault
