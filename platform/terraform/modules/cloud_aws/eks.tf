#https://github.com/terraform-aws-modules/terraform-aws-eks/issues/2635

module "eks" {
  source                         = "terraform-aws-modules/eks/aws"
  version                        = "~>19.16.0"
  cluster_name                   = local.name
  cluster_version                = local.cluster_version
  cluster_endpoint_public_access = true
  cluster_enabled_log_types      = []
  create_cloudwatch_log_group    = false
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  create_aws_auth_configmap = (local.node_group_type == "SELF") ? true : false
  manage_aws_auth_configmap = (local.node_group_type == "SELF") ? true : false
  #
  eks_managed_node_group_defaults = {
    # ami_type                              = "AL2_x86_64"
    # instance_types                        = module.instance_types
    attach_cluster_primary_security_group = true
    #    vpc_security_group_ids                = [aws_security_group.additional.id]
    #   iam_role_additional_policies = {
    # additional = aws_iam_policy.additional.arn
    #}
    node_group_name      = "${local.name}-node-group"
    launch_template_name = "${local.name}-eks-lt-def"
    #    enable_bootstrap_user_data = true

  }

  eks_managed_node_groups = (local.node_group_type == "EKS") ? local.eks_node_groups : []

  #
  self_managed_node_group_defaults = {
    # enable discovery of autoscaling groups by cluster-autoscaler
    autoscaling_group_tags = {
      "k8s.io/cluster-autoscaler/enabled" : true,
      "k8s.io/cluster-autoscaler/${local.name}" : "owned",
    }
    subnet_ids         = module.vpc.private_subnets
    launch_template_os = "amazonlinux2eks"
    k8s_taints         = [{ key = "ondemandInstance", value = "true", effect = "NO_SCHEDULE" }]
    #
    create_iam_role          = true
    iam_role_name            = "${local.name}-sm-ng-iam-role"
    iam_role_use_name_prefix = true
    iam_role_description     = "Def role"
    iam_role_tags = {
      Purpose = "Protector of the kubelet"
    }
    capacity_rebalance   = true
    node_group_name      = "${local.name}-node-group"
    launch_template_name = "${local.name}-lt-def"

  }
  #Still commented out for the safety of stable version
  #self_managed_node_groups = local.node_groups

}
