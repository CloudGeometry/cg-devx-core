
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

  role_name             = "vpc_cni"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }

  tags = local.tags
}

# CSI
module "ebs_csi_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name             = "ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }

  tags = local.tags
}

module "efs_csi_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name             = "efs-csi"
  attach_efs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:efs-csi-controller-sa"]
    }
  }

  tags = local.tags
}
# argo workflow
module "iam_argoworkflow_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "ArgoWorkFlow"

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
# atlantis
module "atlantis_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "atlantis"
  attach_cert_manager_policy = true
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:atlantis"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.atlantis_policy.arn
  }

  tags = local.tags
}

# cert manager
module "cert_manager_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "cert-manager"
  attach_cert_manager_policy = true
  #  cert_manager_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cert-manager"]
    }
  }

  tags = local.tags
}


# container registry
module "image_registry_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "image_registry"
  attach_cert_manager_policy = true
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:harbor"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.image_registry_policy.arn
  }

  tags = local.tags
}

# external DNS
module "external_dns_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "external-dns"
  attach_external_dns_policy = true
  #  external_dns_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:external-dns"]
    }
  }

  tags = local.tags
}
# vault
module "vault_irsa_role" {
  source                     = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name                  = "vault"
  attach_cert_manager_policy = true
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      #need to know ns:serviceaccount
      namespace_service_accounts = ["kube-system:vault"]
    }
  }
  role_policy_arns = {
    policy = aws_iam_policy.vault_policy.arn
  }

  tags = local.tags
}

