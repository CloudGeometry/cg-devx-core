<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_google"></a> [google](#requirement\_google) | ~> 5.40.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.5.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | ~> 5.40.0 |
| <a name="provider_random"></a> [random](#provider\_random) | ~> 3.5.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_cert_manager_sa"></a> [cert\_manager\_sa](#module\_cert\_manager\_sa) | ./modules/sa | n/a |
| <a name="module_ci_sa"></a> [ci\_sa](#module\_ci\_sa) | ./modules/sa | n/a |
| <a name="module_cloud-nat"></a> [cloud-nat](#module\_cloud-nat) | terraform-google-modules/cloud-nat/google | ~> 5.0 |
| <a name="module_external_dns_sa"></a> [external\_dns\_sa](#module\_external\_dns\_sa) | ./modules/sa | n/a |
| <a name="module_gke"></a> [gke](#module\_gke) | terraform-google-modules/kubernetes-engine/google//modules/private-cluster | n/a |
| <a name="module_iac_pr_automation_sa"></a> [iac\_pr\_automation\_sa](#module\_iac\_pr\_automation\_sa) | ./modules/sa | n/a |
| <a name="module_secret_manager_sa"></a> [secret\_manager\_sa](#module\_secret\_manager\_sa) | ./modules/sa | n/a |
| <a name="module_vpc"></a> [vpc](#module\_vpc) | terraform-google-modules/network/google | ~> 9.0.0 |

## Resources

| Name | Type |
|------|------|
| [google_compute_router.router](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router) | resource |
| [google_kms_crypto_key.vault_unseal_key](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/kms_crypto_key) | resource |
| [google_kms_key_ring.vault_key_ring](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/kms_key_ring) | resource |
| [google_project_service.compute_engine_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_project_service.iam_credentials_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_project_service.iam_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_project_service.kms_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_project_service.kubernetes_engine_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_project_service.resource_manager_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_storage_bucket.artifacts_repository](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |
| [random_string.uniq_bucket_suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.uniq_kms_suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [google_client_config.default](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/client_config) | data source |
| [google_project.project](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/project) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_alert_emails"></a> [alert\_emails](#input\_alert\_emails) | n/a | `list(string)` | `[]` | no |
| <a name="input_az_count"></a> [az\_count](#input\_az\_count) | n/a | `number` | `1` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | (Required) Specifies the name of the GKE cluster. | `string` | `"cgdevx"` | no |
| <a name="input_cluster_network_cidr"></a> [cluster\_network\_cidr](#input\_cluster\_network\_cidr) | n/a | `string` | `"10.0.0.0/16"` | no |
| <a name="input_cluster_node_labels"></a> [cluster\_node\_labels](#input\_cluster\_node\_labels) | (Optional) Specifies the GKE node labels | `map(string)` | <pre>{<br>  "provisioned-by": "cg-devx"<br>}</pre> | no |
| <a name="input_cluster_ssh_public_key"></a> [cluster\_ssh\_public\_key](#input\_cluster\_ssh\_public\_key) | (Required) Specifies the SSH public key for GKE worker nodes. | `string` | `""` | no |
| <a name="input_cluster_version"></a> [cluster\_version](#input\_cluster\_version) | (Optional) Specifies the GKE Kubernetes version | `string` | `"1.30"` | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | Specifies the platform domain name | `string` | n/a | yes |
| <a name="input_enable_native_auto_scaling"></a> [enable\_native\_auto\_scaling](#input\_enable\_native\_auto\_scaling) | Enables GKE native autoscaling feature. | `bool` | `false` | no |
| <a name="input_node_groups"></a> [node\_groups](#input\_node\_groups) | n/a | <pre>list(object({<br>    name           = optional(string, "default")<br>    instance_types = optional(list(string), ["n2-standard-2"])<br>    capacity_type  = optional(string, "Regular")<br>    min_size       = optional(number, 1)<br>    max_size       = optional(number, 5)<br>    desired_size   = optional(number, 3)<br>    disk_size      = optional(number, 50)<br>    gpu_enabled    = optional(bool, false)<br>  }))</pre> | <pre>[<br>  {<br>    "capacity_type": "on_demand",<br>    "desired_size": 3,<br>    "disk_size": 50,<br>    "gpu_enabled": false,<br>    "instance_types": [<br>      "n2-standard-2"<br>    ],<br>    "max_size": 5,<br>    "min_size": 1,<br>    "name": "default"<br>  }<br>]</pre> | no |
| <a name="input_region"></a> [region](#input\_region) | Specifies the location for the resource group and all the resources | `string` | `"us-central1"` | no |
| <a name="input_secret_manager_unseal_crypto_key_name"></a> [secret\_manager\_unseal\_crypto\_key\_name](#input\_secret\_manager\_unseal\_crypto\_key\_name) | Name of the key to be used | `string` | `"vault-unseal"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | (Optional) Specifies the GCP resource labels | `map(string)` | <pre>{<br>  "ProvisionedBy": "CGDevX"<br>}</pre> | no |
| <a name="input_workloads"></a> [workloads](#input\_workloads) | Workloads configuration | <pre>map(object({<br>    description = optional(string, "")<br>  }))</pre> | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_artifacts_storage"></a> [artifacts\_storage](#output\_artifacts\_storage) | Continuous Integration Artifact Repository storage backend |
| <a name="output_cert_manager_irsa_role"></a> [cert\_manager\_irsa\_role](#output\_cert\_manager\_irsa\_role) | Certificate Manager IAM role for a K8s service account |
| <a name="output_cluster_autoscaler_irsa_role"></a> [cluster\_autoscaler\_irsa\_role](#output\_cluster\_autoscaler\_irsa\_role) | Cluster Autoscaler IAM Role ARN |
| <a name="output_cluster_certificate_authority_data"></a> [cluster\_certificate\_authority\_data](#output\_cluster\_certificate\_authority\_data) | K8s cluster Certificate Authority certificate data |
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint) | K8s cluster admin API endpoint |
| <a name="output_cluster_node_groups"></a> [cluster\_node\_groups](#output\_cluster\_node\_groups) | Cluster node groups |
| <a name="output_cluster_oidc_issuer_url"></a> [cluster\_oidc\_issuer\_url](#output\_cluster\_oidc\_issuer\_url) | Cluster OIDC provider |
| <a name="output_cluster_oidc_provider_arn"></a> [cluster\_oidc\_provider\_arn](#output\_cluster\_oidc\_provider\_arn) | Cluster OIDC provider stub. |
| <a name="output_external_dns_irsa_role"></a> [external\_dns\_irsa\_role](#output\_external\_dns\_irsa\_role) | External DNS IAM role for a K8s service account |
| <a name="output_iac_pr_automation_irsa_role"></a> [iac\_pr\_automation\_irsa\_role](#output\_iac\_pr\_automation\_irsa\_role) | IaC PR automation service account for a K8s service account |
| <a name="output_iam_ci_irsa_role"></a> [iam\_ci\_irsa\_role](#output\_iam\_ci\_irsa\_role) | Continuous Integration IAM role for K8s service account |
| <a name="output_kube_config_raw"></a> [kube\_config\_raw](#output\_kube\_config\_raw) | Contains the Kubernetes config to be used by kubectl and other compatible tools. |
| <a name="output_network_id"></a> [network\_id](#output\_network\_id) | Platform primary K8s cluster network ID |
| <a name="output_secret_manager_irsa_role"></a> [secret\_manager\_irsa\_role](#output\_secret\_manager\_irsa\_role) | Secrets Manager IAM role for a K8s service account |
| <a name="output_secret_manager_unseal_key"></a> [secret\_manager\_unseal\_key](#output\_secret\_manager\_unseal\_key) | Secret Manager seal key |
| <a name="output_secret_manager_unseal_key_ring"></a> [secret\_manager\_unseal\_key\_ring](#output\_secret\_manager\_unseal\_key\_ring) | Secret Manager unseal key ring |
<!-- END_TF_DOCS -->