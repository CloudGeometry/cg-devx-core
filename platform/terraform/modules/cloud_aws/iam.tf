################################################################################
# Supporting IAM role and policy Resources
################################################################################

# CNI
module "vpc_cni_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name             = "${local.name}-vpc-cni-role"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }

}

# CSI
module "ebs_csi_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name             = "${local.name}-ebs-csi-role"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }

}

module "efs_csi_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name             = "${local.name}-efs-csi-role"
  attach_efs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:efs-csi-controller-sa"]
    }
  }

}

locals {
  ci_sa_workloads_list = [
    for key, value in var.workloads : "wl-${key}-build:argo-workflow"
  ]
}


# Cloud Native CI
module "iam_ci_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name = "${local.name}-ci-role"

  role_policy_arns = {
    policy = aws_iam_policy.ci.arn
  }

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = concat(["argo:argo-workflow", "argo:argo-server"], local.ci_sa_workloads_list)
    }

  }
}

# IaC PR automation
module "iac_pr_automation_irsa_role" {
  source         = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name      = "${local.name}-iac_pr_automation-role"
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["atlantis:atlantis"]
    }
  }
  role_policy_arns = {
    policy               = aws_iam_policy.iac_pr_automation_policy.arn
    administrator_access = "arn:aws:iam::aws:policy/AdministratorAccess"
  }

}

# cert manager
module "cert_manager_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name                  = "${local.name}-cert-manager-role"
  attach_cert_manager_policy = true
  #  cert_manager_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]
  oidc_providers             = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["cert-manager:cert-manager"]
    }
  }

}

# external DNS
module "external_dns_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name                  = "${local.name}-external-dns-role"
  attach_external_dns_policy = true
  #  external_dns_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["external-dns:external-dns"]
    }
  }

}
# secret_manager
module "secret_manager_irsa_role" {
  source         = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name      = "${local.name}-secret_manager-role"
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["vault:vault"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.secret_manager_policy.arn
  }

}

# Cluster Autoscaler
module "cluster_autoscaler_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name                        = "${local.name}-cluster-autoscaler"
  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = [module.eks.cluster_name]

  oidc_providers = {
    ex = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["cluster-autoscaler:cluster-autoscaler"]
    }
  }
}

# Cluster Backups Manager
module "backups_manager_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~>5.58.0"

  role_name = "${local.name}-backups-manager-role"

  role_policy_arns = {
    policy = aws_iam_policy.backups_manager_policy.arn
  }

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["velero:velero"]
    }
  }
}
