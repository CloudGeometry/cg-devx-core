<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.47 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | >= 2.10 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.47 |

## Modules

| Name                                                                                                         | Source | Version |
|--------------------------------------------------------------------------------------------------------------|--------|---------|
| <a name="module_atlantis_irsa_role"></a> [atlantis\_irsa\_role](#module\_atlantis\_irsa\_role)               | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_cert_manager_irsa_role"></a> [cert\_manager\_irsa\_role](#module\_cert\_manager\_irsa\_role) | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_ebs_csi_irsa_role"></a> [ebs\_csi\_irsa\_role](#module\_ebs\_csi\_irsa\_role)                | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_ebs_kms_key"></a> [ebs\_kms\_key](#module\_ebs\_kms\_key)                                    | terraform-aws-modules/kms/aws | ~> 1.5 |
| <a name="module_efs_csi_irsa_role"></a> [efs\_csi\_irsa\_role](#module\_efs\_csi\_irsa\_role)                | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_eks"></a> [eks](#module\_eks)                                                                | terraform-aws-modules/eks/aws | ~>19.16.0 |
| <a name="module_external_dns_irsa_role"></a> [external\_dns\_irsa\_role](#module\_external\_dns\_irsa\_role) | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_iam_argoworkflow_role"></a> [iam\_argoworkflow\_role](#module\_iam\_argoworkflow\_role)      | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_harbor_irsa_role"></a> [image\_registry\_irsa\_role](#module\_image\_registry\_irsa\_role)   | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_vault_irsa_role"></a> [vault\_irsa\_role](#module\_vault\_irsa\_role)                        | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |
| <a name="module_vpc"></a> [vpc](#module\_vpc)                                                                | terraform-aws-modules/vpc/aws | ~> 5.0 |
| <a name="module_vpc_cni_irsa"></a> [vpc\_cni\_irsa](#module\_vpc\_cni\_irsa)                                 | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |

## Resources

| Name                                                                                                                                  | Type |
|---------------------------------------------------------------------------------------------------------------------------------------|------|
| [aws_iam_policy.argoworkflow](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)                 | resource |
| [aws_iam_policy.atlantis_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)              | resource |
| [aws_iam_policy.harbor_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)                | resource |
| [aws_iam_policy.vault_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)                 | resource |
| [aws_ami.eks_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami)                             | data source |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity)         | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | Do we really want the region setting here? | `string` | `"eu-west-1"` | no |
| <a name="input_az_count"></a> [az\_count](#input\_az\_count) | n/a | `number` | `3` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | n/a | `string` | `"gxc"` | no |
| <a name="input_cluster_network_cidr"></a> [cluster\_network\_cidr](#input\_cluster\_network\_cidr) | n/a | `string` | `"10.0.0.0/16"` | no |
| <a name="input_cluster_node_labels"></a> [cluster\_node\_labels](#input\_cluster\_node\_labels) | n/a | `map(any)` | <pre>{<br>  "node.kubernetes.io/node_label1": "value1",<br>  "node.kubernetes.io/node_label2": "value2"<br>}</pre> | no |
| <a name="input_cluster_version"></a> [cluster\_version](#input\_cluster\_version) | n/a | `string` | `"1.27"` | no |
| <a name="input_node_group_type"></a> [node\_group\_type](#input\_node\_group\_type) | n/a | `string` | `"EKS"` | no |
| <a name="input_node_groups"></a> [node\_groups](#input\_node\_groups) | n/a | <pre>list(object({<br>    name           = optional(string, "")<br>    instance_types = optional(list(string), ["t3.medium", "t3.small"])<br>    capacity_type  = optional(string, "on-demand")<br>    min_size       = optional(number, 2)<br>    max_size       = optional(number, 5)<br>    desired_size   = optional(number, 3)<br>    }<br>    )<br>  )</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_atlantis_irsa_role"></a> [atlantis\_irsa\_role](#output\_atlantis\_irsa\_role) | Atlantis admin. IAM Role ARN |
| <a name="output_aws_auth_configmap_yaml"></a> [aws\_auth\_configmap\_yaml](#output\_aws\_auth\_configmap\_yaml) | Formatted yaml output for base aws-auth configmap containing roles used in cluster node groups/fargate profiles |
| <a name="output_az_ids"></a> [az\_ids](#output\_az\_ids) | Availability zones ids |
| <a name="output_cert_manager_irsa_role"></a> [cert\_manager\_irsa\_role](#output\_cert\_manager\_irsa\_role) | Cert\_Manager IAM Role ARN |
| <a name="output_cloudwatch_log_group_arn"></a> [cloudwatch\_log\_group\_arn](#output\_cloudwatch\_log\_group\_arn) | Arn of cloudwatch log group created |
| <a name="output_cloudwatch_log_group_name"></a> [cloudwatch\_log\_group\_name](#output\_cloudwatch\_log\_group\_name) | Name of cloudwatch log group created |
| <a name="output_cluster_addons"></a> [cluster\_addons](#output\_cluster\_addons) | Map of attribute maps for all EKS cluster addons enabled |
| <a name="output_cluster_arn"></a> [cluster\_arn](#output\_cluster\_arn) | The Amazon Resource Name (ARN) of the cluster |
| <a name="output_cluster_certificate_authority_data"></a> [cluster\_certificate\_authority\_data](#output\_cluster\_certificate\_authority\_data) | Base64 encoded certificate data required to communicate with the cluster |
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint) | Endpoint for your Kubernetes API server |
| <a name="output_cluster_iam_role_arn"></a> [cluster\_iam\_role\_arn](#output\_cluster\_iam\_role\_arn) | IAM role ARN of the EKS cluster |
| <a name="output_cluster_iam_role_name"></a> [cluster\_iam\_role\_name](#output\_cluster\_iam\_role\_name) | IAM role name of the EKS cluster |
| <a name="output_cluster_iam_role_unique_id"></a> [cluster\_iam\_role\_unique\_id](#output\_cluster\_iam\_role\_unique\_id) | Stable and unique string identifying the IAM role |
| <a name="output_cluster_id"></a> [cluster\_id](#output\_cluster\_id) | The ID of the EKS cluster. Note: currently a value is returned only for local EKS clusters created on Outposts |
| <a name="output_cluster_identity_providers"></a> [cluster\_identity\_providers](#output\_cluster\_identity\_providers) | Map of attribute maps for all EKS identity providers enabled |
| <a name="output_cluster_name"></a> [cluster\_name](#output\_cluster\_name) | The name of the EKS cluster |
| <a name="output_cluster_oidc_issuer_url"></a> [cluster\_oidc\_issuer\_url](#output\_cluster\_oidc\_issuer\_url) | The URL on the EKS cluster for the OpenID Connect identity provider |
| <a name="output_cluster_platform_version"></a> [cluster\_platform\_version](#output\_cluster\_platform\_version) | Platform version for the cluster |
| <a name="output_cluster_primary_security_group_id"></a> [cluster\_primary\_security\_group\_id](#output\_cluster\_primary\_security\_group\_id) | Cluster security group that was created by Amazon EKS for the cluster. Managed node groups use this security group for control-plane-to-data-plane communication. Referred to as 'Cluster security group' in the EKS console |
| <a name="output_cluster_security_group_arn"></a> [cluster\_security\_group\_arn](#output\_cluster\_security\_group\_arn) | Amazon Resource Name (ARN) of the cluster security group |
| <a name="output_cluster_security_group_id"></a> [cluster\_security\_group\_id](#output\_cluster\_security\_group\_id) | ID of the cluster security group |
| <a name="output_cluster_status"></a> [cluster\_status](#output\_cluster\_status) | Status of the EKS cluster. One of `CREATING`, `ACTIVE`, `DELETING`, `FAILED` |
| <a name="output_cluster_tls_certificate_sha1_fingerprint"></a> [cluster\_tls\_certificate\_sha1\_fingerprint](#output\_cluster\_tls\_certificate\_sha1\_fingerprint) | The SHA1 fingerprint of the public key of the cluster's certificate |
| <a name="output_ebs_csi_irsa_role"></a> [ebs\_csi\_irsa\_role](#output\_ebs\_csi\_irsa\_role) | CSI EBS IAM Role ARN |
| <a name="output_efs_csi_irsa_role"></a> [efs\_csi\_irsa\_role](#output\_efs\_csi\_irsa\_role) | CSI EFS IAM Role ARN |
| <a name="output_eks_managed_node_groups"></a> [eks\_managed\_node\_groups](#output\_eks\_managed\_node\_groups) | Map of attribute maps for all EKS managed node groups created |
| <a name="output_eks_managed_node_groups_autoscaling_group_names"></a> [eks\_managed\_node\_groups\_autoscaling\_group\_names](#output\_eks\_managed\_node\_groups\_autoscaling\_group\_names) | List of the autoscaling group names created by EKS managed node groups |
| <a name="output_external_dns_irsa_role"></a> [external\_dns\_irsa\_role](#output\_external\_dns\_irsa\_role) | External DNS IAM Role ARN |
| <a name="output_iam_argoworkflow_role"></a> [iam\_argoworkflow\_role](#output\_iam\_argoworkflow\_role) | ArgoCD Workflow IAM role ARN |
| <a name="output_igw_arn"></a> [igw\_arn](#output\_igw\_arn) | IGW ARN Generated by VPC module |
| <a name="output_igw_id"></a> [igw\_id](#output\_igw\_id) | IGW ID Generated by VPC module |
| <a name="output_harbor_irsa_role"></a> [image\_registry\_irsa\_role](#output\_image\_registry\_irsa\_role) | Image registry (Harbor) Role ARN |
| <a name="output_kms_key_arn"></a> [kms\_key\_arn](#output\_kms\_key\_arn) | The Amazon Resource Name (ARN) of the key |
| <a name="output_kms_key_id"></a> [kms\_key\_id](#output\_kms\_key\_id) | The globally unique identifier for the key |
| <a name="output_kms_key_policy"></a> [kms\_key\_policy](#output\_kms\_key\_policy) | The IAM resource policy set on the key |
| <a name="output_network_id"></a> [network\_id](#output\_network\_id) | module.vpc.vpc\_id |
| <a name="output_node_security_group_arn"></a> [node\_security\_group\_arn](#output\_node\_security\_group\_arn) | Amazon Resource Name (ARN) of the node shared security group |
| <a name="output_node_security_group_id"></a> [node\_security\_group\_id](#output\_node\_security\_group\_id) | ID of the node shared security group |
| <a name="output_oidc_provider"></a> [oidc\_provider](#output\_oidc\_provider) | The OpenID Connect identity provider (issuer URL without leading `https://`) |
| <a name="output_oidc_provider_arn"></a> [oidc\_provider\_arn](#output\_oidc\_provider\_arn) | The ARN of the OIDC Provider if `enable_irsa = true` |
| <a name="output_private_subnet_id"></a> [private\_subnet\_id](#output\_private\_subnet\_id) | private\_subnet\_id |
| <a name="output_public_subnet_id"></a> [public\_subnet\_id](#output\_public\_subnet\_id) | public\_subnet\_id |
| <a name="output_self_managed_node_groups"></a> [self\_managed\_node\_groups](#output\_self\_managed\_node\_groups) | Map of attribute maps for all self managed node groups created |
| <a name="output_self_managed_node_groups_autoscaling_group_names"></a> [self\_managed\_node\_groups\_autoscaling\_group\_names](#output\_self\_managed\_node\_groups\_autoscaling\_group\_names) | List of the autoscaling group names created by self-managed node groups |
| <a name="output_vault_irsa_role"></a> [vault\_irsa\_role](#output\_vault\_irsa\_role) | AWS Secretsmanager IAM Role ARN |
| <a name="output_vpc_cni_irsa"></a> [vpc\_cni\_irsa](#output\_vpc\_cni\_irsa) | vpc\_cni role ARN |
<!-- END_TF_DOCS -->