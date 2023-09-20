data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}
locals {
  name                = var.cluster_name
  cluster_version     = var.cluster_version
  region              = var.region
  aws_account         = data.aws_caller_identity.current.account_id
  vpc_cidr            = var.cluster_network_cidr
  azs                 = slice(data.aws_availability_zones.available.names, 0, min(var.az_count, length(data.aws_availability_zones.available.names)))
  cluster_node_lables = var.cluster_node_labels
  node_group_type     = var.node_group_type
  tags = {
    cgx_name = local.name
  }
  node_labels_substr      = join(",", formatlist("%s=%s", keys(var.cluster_node_labels), values(var.cluster_node_labels)))
  default_node_group_name = "${local.name}-node-group"
  eks_node_groups = [
    for node_group in var.node_groups :
    {
      name           = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size       = node_group.min_size
      max_size       = node_group.max_size
      desired_size   = node_group.desired_size
      instance_types = node_group.instance_types
      capacity_type  = upper(node_group.capacity_type)
      labels = merge(
        { "node.kubernetes.io/lifecycle" = "${node_group.capacity_type}" },
        var.cluster_node_labels
      )



    }
  ]

  sm_node_groups = [
    for node_group in var.node_groups :
    {
      name                    = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size                = node_group.min_size
      max_size                = node_group.max_size
      desired_size            = node_group.desired_size
      override_instance_types = node_group.instance_types
      instance_type           = node_group.instance_types[0]
      instance_types          = node_group.instance_types
      instance_market_options = ((upper(node_group.capacity_type) == "spot") && (local.node_group_type == "SELF")) ? { market_type = "spot" } : {}
      capacity_type           = upper(node_group.capacity_type)
      bootstrap_extra_args = join(",", [
        "--kubelet-extra-args '--node-labels=node.kubernetes.io/lifecycle=${node_group.capacity_type}",
        local.node_labels_substr
        ,
        "'"
        ]
      )

    }
  ]
} #end of locals


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
}

