################################################################################
# EKS Module
################################################################################

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  #pin module version
  version = "19.10.0"

  tags = local.tags
}
