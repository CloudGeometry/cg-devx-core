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

  # Self managed node groups will not automatically create the aws-auth configmap so we need to
  create_aws_auth_configmap = true
  manage_aws_auth_configmap = true

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
    iam_role_name            = "${local.name}-self-managed-node-group-iam-role"
    iam_role_use_name_prefix = true
    iam_role_description     = "Def role"
    iam_role_tags = {
      Purpose = "Protector of the kubelet"
    }
    capacity_rebalance   = true
    node_group_name      = "${local.name}-node-group"
    launch_template_name = "${local.name}-lt-def"

  }
  /*has to be replaced with iteration through array of objects*/
  /*
  self_managed_node_groups = {
    # Default node group - as provisioned by the module defaults
    #    default_node_group = {}
    test_ng_dmd = {
      #
      node_group_name = "smng-demand"
      capacity_type   = "on-demand"
      #instance_types     = ["t3.medium", "t3.small"]
      instance_types = "t3.medium"
      min_size       = 2
      max_size       = 5
      desired_size   = 3

    }

  }
  */
  self_managed_node_groups = local.node_groups
}
