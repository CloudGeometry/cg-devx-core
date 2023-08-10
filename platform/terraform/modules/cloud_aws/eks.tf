module "eks" {
  source                         = "terraform-aws-modules/eks/aws"
  version                        = "~>19.16.0"
  cluster_name                   = local.name
  cluster_version                = local.cluster_version
  cluster_endpoint_public_access = true
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
  }
  /*has to be replaced with iteration through array of objects*/
  self_managed_node_groups = {
    # Default node group - as provisioned by the module defaults
    #    default_node_group = {}
    test_ng_dmd = {
      #
      node_group_name    = "smng-demand"
      capacity_type      = "on-demand"
      capacity_rebalance = true
      #instance_types     = ["t3.medium", "t3.small"]
      instance_type      = "t3.medium"
      min_size           = 2
      max_size           = 5
      desired_size       = 3
      subnet_ids         = module.vpc.private_subnets
      launch_template_os = "amazonlinux2eks"
      k8s_taints         = [{ key = "ondemandInstance", value = "true", effect = "NO_SCHEDULE" }]
      #
      create_iam_role          = true
      iam_role_name            = "self-managed-node-group-iam-role"
      iam_role_use_name_prefix = false
      iam_role_description     = "Self managed node group complete example role"
      iam_role_tags = {
        Purpose = "Protector of the kubelet"
      }
      iam_role_additional_policies = {
        AmazonEC2ContainerRegistryReadOnly = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        additional                         = aws_iam_policy.additional.arn
      }

    }

  }
}
