###
output "network_id" {
  description = "module.vpc.vpc_id"
  value       = module.vpc.vpc_id
}
output "public_subnet_id" {
  description = "public_subnet_id"
  value       = module.vpc.public_subnets
}
output "private_subnet_id" {
  description = "private_subnet_id"
  value       = module.vpc.private_subnets
}
output "az_ids" {
  description = "Availability zones ids"
  value       = module.vpc.azs
}
output "kms_key_id" {
  description = "The globally unique identifier for the key"
  value       = module.eks.kms_key_id
}
#put roles arns here
output "vpc_cni_irsa" {
  description = "vpc_cni role ARN"
  value       = module.vpc_cni_irsa.iam_role_arn
}
output "ebs_csi_irsa_role" {
  description = "CSI EBS IAM Role ARN"
  value       = module.ebs_csi_irsa_role.iam_role_arn
}

output "efs_csi_irsa_role" {
  description = "CSI EFS IAM Role ARN"
  value       = module.efs_csi_irsa_role.iam_role_arn
}
output "iam_ci_irsa_role" {
  description = "Cloud Native CI IAM role ARN"
  value       = module.iam_ci_role.iam_role_arn
}
output "iac_pr_automation_irsa_role" {
  description = "IaC PR automation IAM Role ARN"
  value       = module.iac_pr_automation_irsa_role.iam_role_arn
}
output "cert_manager_irsa_role" {
  description = "Cert Manager IAM Role ARN"
  value       = module.cert_manager_irsa_role.iam_role_arn
}
output "external_dns_irsa_role" {
  description = "External DNS IAM Role ARN"
  value       = module.external_dns_irsa_role.iam_role_arn
}
output "secret_manager_irsa_role" {
  description = "AWS Secretsmanager IAM Role ARN"
  value       = module.secret_manager_irsa_role.iam_role_arn
}
output "cluster_autoscaler_irsa_role" {
  description = "Cluster Autoscaler IAM Role ARN"
  value       = module.cluster_autoscaler_irsa_role.iam_role_arn
}
output "backups_manager_irsa_role" {
  description = "Cluster Backup Manager IAM role for a K8s service account"
  value       = module.backups_manager_irsa_role.iam_role_arn
}


################################################################################
# Cluster
################################################################################

output "cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster"
  value       = module.eks.cluster_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_endpoint" {
  description = "Endpoint for your Kubernetes API server"
  value       = module.eks.cluster_endpoint
}

output "cluster_id" {
  description = "The ID of the EKS cluster. Note: currently a value is returned only for local EKS clusters created on Outposts"
  value       = module.eks.cluster_id
}

output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.eks.cluster_oidc_issuer_url
  sensitive   = true
}

output "cluster_platform_version" {
  description = "Platform version for the cluster"
  value       = module.eks.cluster_platform_version
}

output "cluster_status" {
  description = "Status of the EKS cluster. One of `CREATING`, `ACTIVE`, `DELETING`, `FAILED`"
  value       = module.eks.cluster_status
}

output "cluster_primary_security_group_id" {
  description = "Cluster security group that was created by Amazon EKS for the cluster. Managed node groups use this security group for control-plane-to-data-plane communication. Referred to as 'Cluster security group' in the EKS console"
  value       = module.eks.cluster_primary_security_group_id
}

output "cluster_node_groups" {
  value       = var.node_groups
  description = "Cluster node groups"
}

################################################################################
# KMS Key
################################################################################

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the key"
  value       = module.eks.kms_key_arn
}
/*
output "kms_key_id" {
  description = "The globally unique identifier for the key"
  value       = module.eks.kms_key_id
}
*/
output "kms_key_policy" {
  description = "The IAM resource policy set on the key"
  value       = module.eks.kms_key_policy
}

output "secret_manager_unseal_key_ring" {
  value       = ""
  description = "Secret Manager unseal key ring"
  sensitive   = true
}

################################################################################
# Security Group
################################################################################

output "cluster_security_group_arn" {
  description = "Amazon Resource Name (ARN) of the cluster security group"
  value       = module.eks.cluster_security_group_arn
}

output "cluster_security_group_id" {
  description = "ID of the cluster security group"
  value       = module.eks.cluster_security_group_id
}

################################################################################
# Node Security Group
################################################################################

output "node_security_group_arn" {
  description = "Amazon Resource Name (ARN) of the node shared security group"
  value       = module.eks.node_security_group_arn
}

output "node_security_group_id" {
  description = "ID of the node shared security group"
  value       = module.eks.node_security_group_id
}

################################################################################
# IRSA
################################################################################
output "cluster_oidc_provider_url" {
  description = "The OpenID Connect identity provider (issuer URL without leading `https://`)"
  value       = module.eks.oidc_provider
}

output "cluster_oidc_provider_arn" {
  description = "The ARN of the OIDC Provider if `enable_irsa = true`"
  value       = module.eks.oidc_provider_arn
}

output "cluster_tls_certificate_sha1_fingerprint" {
  description = "The SHA1 fingerprint of the public key of the cluster's certificate"
  value       = module.eks.cluster_tls_certificate_sha1_fingerprint
}

################################################################################
# IAM Role
################################################################################

output "cluster_iam_role_name" {
  description = "IAM role name of the EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN of the EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_iam_role_unique_id" {
  description = "Stable and unique string identifying the IAM role"
  value       = module.eks.cluster_iam_role_unique_id
}

################################################################################
# EKS Addons
################################################################################

output "cluster_addons" {
  description = "Map of attribute maps for all EKS cluster addons enabled"
  value       = module.eks.cluster_addons
}

################################################################################
# EKS Identity Provider
################################################################################

output "cluster_identity_providers" {
  description = "Map of attribute maps for all EKS identity providers enabled"
  value       = module.eks.cluster_identity_providers
}

################################################################################
# CloudWatch Log Group
################################################################################

output "cloudwatch_log_group_name" {
  description = "Name of cloudwatch log group created"
  value       = module.eks.cloudwatch_log_group_name
}

output "cloudwatch_log_group_arn" {
  description = "Arn of cloudwatch log group created"
  value       = module.eks.cloudwatch_log_group_arn
}

################################################################################
# Self Managed Node Group
################################################################################

output "self_managed_node_groups" {
  description = "Map of attribute maps for all self managed node groups created"
  value       = module.eks.self_managed_node_groups
}

output "self_managed_node_groups_autoscaling_group_names" {
  description = "List of the autoscaling group names created by self-managed node groups"
  value       = module.eks.self_managed_node_groups_autoscaling_group_names
}
#

################################################################################
# EKS Managed Node Group
################################################################################

output "eks_managed_node_groups" {
  description = "Map of attribute maps for all EKS managed node groups created"
  value       = module.eks.eks_managed_node_groups
}
output "eks_managed_node_groups_autoscaling_group_names" {
  description = "List of the autoscaling group names created by EKS managed node groups"
  value       = module.eks.eks_managed_node_groups_autoscaling_group_names
}


################################################################################
# Additional
################################################################################

output "aws_auth_configmap_yaml" {
  description = "Formatted yaml output for base aws-auth configmap containing roles used in cluster node groups/fargate profiles"
  value       = module.eks.aws_auth_configmap_yaml
}
output "igw_arn" {
  description = "IGW ARN Generated by VPC module"
  value       = module.vpc.igw_arn
}
output "igw_id" {
  description = "IGW ID Generated by VPC module"
  value       = module.vpc.igw_id
}
output "secret_manager_unseal_key" {
  description = "The globally unique identifier for the secret manager key"
  value       = module.secret_manager_unseal_kms_key.key_id
}

output "artifacts_storage" {
  description = "The artifact storage S3 bucket name"
  value       = module.artifacts_repository.s3_bucket_id
}

output "artifacts_storage_endpoint" {
  description = "The artifact storage S3 bucket domain name"
  value       = module.artifacts_repository.s3_bucket_bucket_domain_name
}

output "backups_storage" {
  description = "The backups storage S3 bucket name"
  value       = module.backups_repository.s3_bucket_id
}

# stub value for module compatibility
output "artifacts_storage_access_key" {
  value       = ""
  sensitive   = true
  description = "Continuous Integration Artifact Repository storage account primary access key"
}

# stub value for module compatibility
output "kube_config_raw" {
  value       = ""
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}

# stub value for module compatibility
output "storage_account" {
  description = "The backups storage account name"
  value       = ""
}

# stub value for module compatibility
output "resource_group" {
  value       = ""
  description = "Resource group name"
}

# stub value for module compatibility
output "node_resource_group" {
  value       = ""
  description = "Node resource group name"
}

