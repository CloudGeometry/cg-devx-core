# Platform IaC - Cloud Infrastructure

This is a platform Infrastructure as Code (IaC) Cloud Infrastructure main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

## Cloud provisioning module parameter

### Input

```terraform
# cloud region
region               = "provider specific"
# K8s cluster network CIDR
cluster_network_cidr = "10.0.0.0/16"
# K8s cluster name
cluster_name         = "cgdevx"
# Number of availability zones
az_count             = 3
# K8s cluster version
cluster_version      = "provider specific"
# array, represents K8s node groups
node_groups          = [
  {
    # optional, node group name
    name           = "default"
    # compute node type (size), will fall back to the next value when the
    # first specified instance type is not available, 
    # could be used in combination with capacity_type = "spot"
    instance_types = ["provider specific"]
    # min node count for cluster
    min_size       = 3
    # max node count for cluster
    max_size       = 5
    # desired node count for cluster
    desired_size   = 3
    # "on-demand" or "spot"
    capacity_type  = "ON_DEMAND"
  }
]
# K8s node labels
cluster_node_labels = ["cgdevx"]
# ssh public keys used to connect to nodes
ssh_public_key      = ""
# list of emails subscribed to cloud native resource downtime alarms
alert_emails        = [""]


```

### Output

| Name                                                                                                                                             | Description                                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| <a name="output_artifact_storage"></a> [artifact\_storage](#output\_artifact\_storage)                                                           | Continuous Integration Artifact Repository storage backend |
| <a name="output_cert_manager_role"></a> [cert\_manager\_role](#output\_cert\_manager\_role)                                                      | Certificate Manager IAM role for a K8s service account     |
| <a name="output_cluster_certificate_authority_data"></a> [cluster\_certificate\_authority\_data](#output\_cluster\_certificate\_authority\_data) | K8s cluster Certificate Authority certificate data         |
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint)                                                           | K8s cluster admin API endpoint                             |
| <a name="output_external_dns_role"></a> [external\_dns\_role](#output\_external\_dns\_role)                                                      | External DNS IAM role for a K8s service account            |
| <a name="output_iac_pr_automation_role"></a> [iac\_pr\_automation\_role](#output\_iac\_pr\_automation\_role)                                     | IaC PR automation IAM role for a K8s service account       |
| <a name="output_iam_ci_role"></a> [iam\_ci\_role](#output\_iam\_ci\_role)                                                                        | Continuous Integration IAM role for K8s service account    |
| <a name="output_network_id"></a> [network\_id](#output\_network\_id)                                                                             | Platform primary K8s cluster network ID                    |
| <a name="output_secret_manager_role"></a> [secret\_manager\_role](#output\_secret\_manager\_role)                                                | Secrets Manager IAM role for a K8s service account         |
| <a name="output_secret_manager_seal_key"></a> [secret\_manager\_seal\_key](#output\_secret\_manager\_seal\_key)                                  | Secret Manager seal key                                    |
