module "secret_manager_unseal_kms_key" {
  depends_on = [module.secret_manager_irsa_role, module.iac_pr_automation_irsa_role]

  source  = "terraform-aws-modules/kms/aws"
  version = "~> 1.5"

  description = "CG DevX secret manager unseal key"

  # Key Policy
  key_users          = [module.secret_manager_irsa_role.iam_role_arn]
  key_administrators = [module.iac_pr_automation_irsa_role.iam_role_arn]
  key_owners         = [module.iac_pr_automation_irsa_role.iam_role_arn]

  # Aliases
  aliases = ["eks/${local.name}/secret-manager"]
}

module "ebs_kms_key" {
  depends_on = [module.iac_pr_automation_irsa_role, module.eks]

  source  = "terraform-aws-modules/kms/aws"
  version = "~> 1.5"

  description = "Customer managed key to encrypt EKS managed node group volumes"

  # Key Policy
  key_administrators = [module.iac_pr_automation_irsa_role.iam_role_arn]
  key_owners         = [module.iac_pr_automation_irsa_role.iam_role_arn]

  key_service_roles_for_autoscaling = [
    # required for the ASG to manage encrypted volumes for nodes
    "arn:aws:iam::${local.aws_account}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling",
    # required for the cluster / persistentvolume-controller to create encrypted PVCs
    module.eks.cluster_iam_role_arn,
  ]

  # Aliases
  aliases = ["eks/${local.name}/ebs"]
}

