
################################################################################
# Supporting IAM role and policy Resources
################################################################################
/*
module "sample_role" {
  source  = "terraform-aws-modules/iam/aws/modules/iam-role-for-service-accounts-eks"
  version = "5.20.0"
  tags = local.tags
}

resource "aws_iam_policy" "sample_policy" {

  policy = <<EOT
EOT
}
*/

#Need create roles and policies for
# CNI
module "vpc_cni_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

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

  role_name             = "${local.name}-efs-csi-role"
  attach_efs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:efs-csi-controller-sa"]
    }
  }

}
# argo workflow
module "iam_argoworkflow_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "${local.name}-argoworkflow-role"

  role_policy_arns = {
    policy = aws_iam_policy.argoworkflow.arn
  }

  oidc_providers = {
    main = {
      provider_arn               = "module.eks.oidc_provider_arn"
      namespace_service_accounts = ["default:argo"]
    }

  }
}
# argocd
module "iam_argocd_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "${local.name}-argocd-role"

  role_policy_arns = {
    policy = aws_iam_policy.argocd.arn
  }

  oidc_providers = {
    main = {
      provider_arn               = "module.eks.oidc_provider_arn"
      namespace_service_accounts = ["default:argocd"]
    }

  }
}
# atlantis
module "iac_pr_automation_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "${local.name}-iac_pr_automation-role"
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:atlantis"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.iac_pr_automation_policy.arn
  }

}

# cert manager
module "cert_manager_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "${local.name}-cert-manager-role"
  attach_cert_manager_policy = true
  #  cert_manager_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cert-manager"]
    }
  }

}


# container registry
module "registry_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "${local.name}-image-registry-role"
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:harbor"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.registry_policy.arn
  }
}

# external DNS
module "external_dns_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "${local.name}-external-dns-role"
  attach_external_dns_policy = true
  #  external_dns_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:external-dns"]
    }
  }

}
# vault
module "secret_manager_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "${local.name}-secret_manager-role"
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:vault"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.secret_manager_policy.arn
  }

}

