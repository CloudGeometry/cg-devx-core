data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}
locals {
  name                    = var.cluster_name
  cluster_version         = var.cluster_version
  region                  = var.region
  aws_account             = data.aws_caller_identity.current.account_id
  vpc_cidr                = var.cluster_network_cidr
  azs                     = slice(data.aws_availability_zones.available.names, 0, min(var.az_count, length(data.aws_availability_zones.available.names)))
  cluster_node_lables     = var.cluster_node_labels
  node_group_type         = var.node_group_type
  tags                    = var.tags
  node_labels_substr      = join(",", formatlist("%s=%s", keys(var.cluster_node_labels), values(var.cluster_node_labels)))
  default_node_group_name = "${local.name}-node-group"
  eks_node_groups         = [
    for node_group in var.node_groups :
    {
      name           = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size       = node_group.min_size
      max_size       = node_group.max_size
      desired_size   = node_group.desired_size
      disk_size      = node_group.disk_size
      instance_types = node_group.instance_types
      capacity_type  = upper(node_group.capacity_type)
      labels         = merge(
        var.cluster_node_labels,
        { "node.kubernetes.io/lifecycle" = "${node_group.capacity_type}" }
      )
      ami_type = node_group.gpu_enabled == true ? "BOTTLEROCKET_x86_64_NVIDIA" : "AL2023_x86_64_STANDARD"
      taints   = merge(node_group.capacity_type == "spot" ?
        {
          capacity_type_spot = {
            key    = "capacity-type-spot"
            value  = "true"
            effect = "PREFER_NO_SCHEDULE"
          }
        } :
        {
        },
          node_group.gpu_enabled == true ? {
          group_type = {
            key    = "group-type"
            value  = "gpu-enabled"
            effect = "NO_SCHEDULE"
          }
        } : {}
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
      instance_market_options = ((upper(node_group.capacity_type) == "spot") && (local.node_group_type == "SELF")) ? {
        market_type = "spot"
      } : {}
      capacity_type        = upper(node_group.capacity_type)
      bootstrap_extra_args = join(",", [
        "--kubelet-extra-args '--node-labels=node.kubernetes.io/lifecycle=${node_group.capacity_type}",
        local.node_labels_substr,
        "'"
      ]
      )
      taints = merge(node_group.capacity_type == "spot" ?
        {
          capacity_type_spot = {
            key    = "capacity-type-spot"
            value  = "true"
            effect = "PREFER_NO_SCHEDULE"
          }
        } :
        {
        },
          node_group.gpu_enabled == true ? {
          group_type = {
            key    = "group-type"
            value  = "gpu-enabled"
            effect = "NO_SCHEDULE"
          }
        } : {}
      )
    }
  ]
}
#end of locals

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
