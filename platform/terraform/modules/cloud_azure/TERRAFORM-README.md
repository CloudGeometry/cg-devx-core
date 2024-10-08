<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~>3.86 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~>3.5.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | ~>3.86 |
| <a name="provider_http"></a> [http](#provider\_http) | n/a |
| <a name="provider_random"></a> [random](#provider\_random) | ~>3.5.1 |
| <a name="provider_time"></a> [time](#provider\_time) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_cert_manager_sa"></a> [cert\_manager\_sa](#module\_cert\_manager\_sa) | ./modules/aks_rbac | n/a |
| <a name="module_ci_sa"></a> [ci\_sa](#module\_ci\_sa) | ./modules/aks_rbac | n/a |
| <a name="module_cluster_autoscaler_sa"></a> [cluster\_autoscaler\_sa](#module\_cluster\_autoscaler\_sa) | ./modules/aks_rbac | n/a |
| <a name="module_external_dns_sa"></a> [external\_dns\_sa](#module\_external\_dns\_sa) | ./modules/aks_rbac | n/a |
| <a name="module_iac_pr_automation_sa"></a> [iac\_pr\_automation\_sa](#module\_iac\_pr\_automation\_sa) | ./modules/aks_rbac | n/a |
| <a name="module_secret_manager_sa"></a> [secret\_manager\_sa](#module\_secret\_manager\_sa) | ./modules/aks_rbac | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_key_vault.key_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault) | resource |
| [azurerm_key_vault_key.secret_manager_unseal_kms_key](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_key) | resource |
| [azurerm_kubernetes_cluster.aks_cluster](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster) | resource |
| [azurerm_kubernetes_cluster_node_pool.node_pool](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster_node_pool) | resource |
| [azurerm_log_analytics_solution.container_insights_solution](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_solution) | resource |
| [azurerm_log_analytics_workspace.log_analytics_workspace](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_workspace) | resource |
| [azurerm_private_dns_zone.blob_storage_private](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone.key_vault_private](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone_virtual_network_link.blob_storage_private_link](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_dns_zone_virtual_network_link.key_vault_private_link](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_endpoint.blob_private_endpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.key_vault_private_endpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_resource_group.rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_role_assignment.rbac_keyvault_administrator](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_storage_account.storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_container.artifacts_repository](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container) | resource |
| [azurerm_subnet.internal_subnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |
| [azurerm_subnet.private_subnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |
| [azurerm_subnet.public_subnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |
| [azurerm_user_assigned_identity.aks_identity](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/user_assigned_identity) | resource |
| [azurerm_virtual_network.vnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_network) | resource |
| [random_string.key_random_suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.sa_random_suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.sc_random_suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [time_sleep.wait_subnet](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [azurerm_client_config.client_identity](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
| [http_http.runner_ip_address](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_alert_emails"></a> [alert\_emails](#input\_alert\_emails) | n/a | `list(string)` | `[]` | no |
| <a name="input_az_count"></a> [az\_count](#input\_az\_count) | n/a | `number` | `1` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | (Required) Specifies the name of the AKS cluster. | `string` | `"CGDevX"` | no |
| <a name="input_cluster_network_cidr"></a> [cluster\_network\_cidr](#input\_cluster\_network\_cidr) | n/a | `string` | `"10.1.0.0/16"` | no |
| <a name="input_cluster_node_labels"></a> [cluster\_node\_labels](#input\_cluster\_node\_labels) | (Optional) Specifies the AKS node labels | `map(string)` | <pre>{<br>  "provisioned-by": "cg-devx"<br>}</pre> | no |
| <a name="input_cluster_ssh_public_key"></a> [cluster\_ssh\_public\_key](#input\_cluster\_ssh\_public\_key) | (Required) Specifies the SSH public key for AKS worker nodes. | `string` | `""` | no |
| <a name="input_cluster_version"></a> [cluster\_version](#input\_cluster\_version) | (Optional) Specifies the AKS Kubernetes version | `string` | `"1.30"` | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | Specifies the platform domain name | `string` | n/a | yes |
| <a name="input_enable_native_auto_scaling"></a> [enable\_native\_auto\_scaling](#input\_enable\_native\_auto\_scaling) | Enables AKS native autoscaling feature. | `bool` | `false` | no |
| <a name="input_node_groups"></a> [node\_groups](#input\_node\_groups) | n/a | <pre>list(object({<br>    name           = optional(string, "default")<br>    instance_types = optional(list(string), ["Standard_B2ms"])<br>    capacity_type  = optional(string, "Regular")<br>    min_size       = optional(number, 3)<br>    max_size       = optional(number, 5)<br>    desired_size   = optional(number, 3)<br>    disc_size      = optional(number, 50)<br>    gpu_enabled    = optional(bool, false)<br>  }))</pre> | <pre>[<br>  {<br>    "capacity_type": "on_demand",<br>    "desired_size": 3,<br>    "instance_types": [<br>      "Standard_B2ms"<br>    ],<br>    "max_size": 5,<br>    "min_size": 3,<br>    "name": "default"<br>  }<br>]</pre> | no |
| <a name="input_region"></a> [region](#input\_region) | Specifies the location for the resource group and all the resources | `string` | `"westeurope"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | (Optional) Specifies the Azure resource tags | `map(string)` | <pre>{<br>  "provisioned-by": "cg-devx"<br>}</pre> | no |
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
| <a name="output_iac_pr_automation_irsa_role"></a> [iac\_pr\_automation\_irsa\_role](#output\_iac\_pr\_automation\_irsa\_role) | IaC PR automation IAM role for a K8s service account |
| <a name="output_iam_ci_irsa_role"></a> [iam\_ci\_irsa\_role](#output\_iam\_ci\_irsa\_role) | Continuous Integration IAM role for K8s service account |
| <a name="output_kube_config_raw"></a> [kube\_config\_raw](#output\_kube\_config\_raw) | Contains the Kubernetes config to be used by kubectl and other compatible tools. |
| <a name="output_network_id"></a> [network\_id](#output\_network\_id) | Platform primary K8s cluster network ID |
| <a name="output_secret_manager_irsa_role"></a> [secret\_manager\_irsa\_role](#output\_secret\_manager\_irsa\_role) | Secrets Manager IAM role for a K8s service account |
| <a name="output_secret_manager_unseal_key"></a> [secret\_manager\_unseal\_key](#output\_secret\_manager\_unseal\_key) | Secret Manager unseal key |
| <a name="output_secret_manager_unseal_key_ring"></a> [secret\_manager\_unseal\_key\_ring](#output\_secret\_manager\_unseal\_key\_ring) | Secret Manager unseal key ring |
<!-- END_TF_DOCS -->