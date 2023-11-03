#https://github.com/terraform-aws-modules/terraform-aws-eks/issues/2635

module "eks" {
  source                         = "terraform-aws-modules/eks/aws"
  version                        = "~>19.16.0"
  cluster_name                   = local.name
  cluster_version                = local.cluster_version
  cluster_endpoint_public_access = true
  cluster_enabled_log_types      = []
  create_cloudwatch_log_group    = false

  # KMS configuration
  kms_key_enable_default_policy   = true
  kms_key_deletion_window_in_days = 7
  # TODO: temp shortcut to avoid 2 step initialisation as circular dependency is created when referencing role
  kms_key_administrators          = ["*"]
  # kms_key_administrators         = ["arn:aws:iam::${local.aws_account}:role/${local.name}-iac_pr_automation-role"]
  # kms_key_owners                 = ["arn:aws:iam::${local.aws_account}:role/${local.name}-iac_pr_automation-role"]

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent              = true
      service_account_role_arn = module.vpc_cni_irsa.iam_role_arn
      configuration_values     = jsonencode({
        env = {
          # Reference docs https://docs.aws.amazon.com/eks/latest/userguide/cni-increase-ip-addresses.html
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET       = "1"
        }
      })
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = module.ebs_csi_irsa_role.iam_role_arn
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  create_aws_auth_configmap       = (local.node_group_type == "SELF") ? true : false
  manage_aws_auth_configmap       = (local.node_group_type == "SELF") ? true : false
  #
  create_node_security_group      = false
  eks_managed_node_group_defaults = {
    # ami_type                              = "AL2_x86_64"
    # instance_types                        = module.instance_types
    attach_cluster_primary_security_group = true
    node_group_name                       = "${local.name}-node-group"
    use_custom_launch_template            = false

  }

  eks_managed_node_groups = (local.node_group_type == "EKS") ? local.eks_node_groups : []

  #
  self_managed_node_group_defaults = {
    # enable discovery of autoscaling groups by cluster-autoscaler
    autoscaling_group_tags = {
      "k8s.io/cluster-autoscaler/enabled" : true,
      "k8s.io/cluster-autoscaler/${local.name}" : "owned",
    }
    subnet_ids               = module.vpc.private_subnets
    launch_template_os       = "amazonlinux2eks"
    k8s_taints               = [{ key = "ondemandInstance", value = "true", effect = "NO_SCHEDULE" }]
    #
    create_iam_role          = true
    iam_role_name            = "${local.name}-sm-ng-iam-role"
    iam_role_use_name_prefix = true
    iam_role_description     = "Def role"
    iam_role_tags            = {
      Purpose = "Protector of the kubelet"
    }
    capacity_rebalance   = true
    node_group_name      = "${local.name}-node-group"
    launch_template_name = "${local.name}-lt-def"

  }
  #Still commented out for the safety of stable version
  #self_managed_node_groups = local.node_groups

}

# key-pair for custom launch template
#resource "aws_key_pair" "eks_nodes" {
#  key_name   = "${local.name}-eks-nodes"
#  public_key = var.ssh_public_key
#}
#
#resource "aws_launch_template" "eks_node_with_keypair" {
#  instance_type = coalesce(first(local.eks_node_groups[0].instance_types), "t3.medium")
#  key_name = aws_key_pair.eks_nodes.key_name
#}