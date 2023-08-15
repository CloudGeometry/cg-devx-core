provider "aws" {
  region  = local.region
  profile = local.aws_account
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}
locals {
  #  name            = "ex-${replace(basename(path.cwd), "_", "-")}"
  name                = var.cluster_name
  cluster_version     = var.cluster_version
  region              = var.aws_region
  aws_account         = var.aws_account
  vpc_cidr            = var.cluster_network_cidr
  azs                 = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  cluster_node_lables = var.cluster_node_labels

  tags = {
    cgx_name   = local.name
    GithubRepo = "terraform-aws-eks"
    GithubOrg  = "terraform-aws-modules"
  }
  default_node_group_name = "${local.name}-node-group"
  node_groups = [
    for node_group in var.node_groups :
    {
      name                    = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size                = node_group.min_size
      max_size                = node_group.max_size
      desired_size            = node_group.desired_size
      override_instance_types = node_group.instance_types
      instance_type           = node_group.instance_types[0]
      #node_group.capacity_type == "spot" ? instance_market_options.market_type = "spot" : {} 
      instance_market_options = lower(node_group.capacity_type) == "spot" ? { market_type = "spot" } : {}
      bootstrap_extra_args = join(",", [
        "--kubelet-extra-args '--node-labels=node.kubernetes.io/lifecycle=${node_group.capacity_type}",
        var.cluster_node_labels,
        "'"
        ]
      )

    }
  ]

  #  node_groups = var.node_groups
  /*
  node_groups = { for node_group in var.node_groups : node_group.name => {
    node_group_name = node_group.name
    capacity_type   = node_group.capacity_type
    #instance_types     = ["t3.medium", "t3.small"]
    instance_types = node_group.instance_types
    min_size       = 2
    max_size       = 5
    desired_size   = 3
    name_prefix = "def_group_np-"

    }
  }
*/
}
################################################################################
# EKS Module
################################################################################


################################################################################
# Supporting Resources
################################################################################



data "aws_ami" "eks_default" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amazon-eks-node-${local.cluster_version}-v*"]
  }
}


module "key_pair" {
  source             = "terraform-aws-modules/key-pair/aws"
  version            = "~> 2.0"
  key_name_prefix    = local.name
  create_private_key = true
  tags               = local.tags
}

module "ebs_kms_key" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 1.5"

  description = "Customer managed key to encrypt EKS managed node group volumes"

  # Policy
  key_administrators = [
    data.aws_caller_identity.current.arn
  ]

  key_service_roles_for_autoscaling = [
    # required for the ASG to manage encrypted volumes for nodes
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling",
    # required for the cluster / persistentvolume-controller to create encrypted PVCs
    module.eks.cluster_iam_role_arn,
  ]

  # Aliases
  aliases = ["eks/${local.name}/ebs"]

  tags = local.tags
}

