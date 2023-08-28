################################################################################
# Supporting  Network Resources
################################################################################

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "4.0.2"

# configuration
  tags = local.tags
}

# input parameters
# VPC name 
# CIDR
# tags