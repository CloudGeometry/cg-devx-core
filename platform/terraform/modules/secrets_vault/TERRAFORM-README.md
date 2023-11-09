<!-- BEGIN_TF_DOCS -->

## Requirements

| Name                                                    | Version |
|---------------------------------------------------------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.47 |

## Providers

| Name                                                       | Version |
|------------------------------------------------------------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws)          | >= 4.47 |
| <a name="provider_random"></a> [random](#provider\_random) | n/a     |
| <a name="provider_vault"></a> [vault](#provider\_vault)    | n/a     |

## Modules

| Name                                                            | Source           | Version |
|-----------------------------------------------------------------|------------------|---------|
| <a name="module_argo"></a> [argo](#module\_argo)                | ./oidc-client    | n/a     |
| <a name="module_argocd"></a> [argocd](#module\_argocd)          | ./oidc-client    | n/a     |
| <a name="module_grafana"></a> [grafana](#module\_grafana)       | ./oidc-client    | n/a     |
| <a name="module_harbor"></a> [harbor](#module\_harbor)          | ./oidc-client    | n/a     |
| <a name="module_sonarqube"></a> [sonarqube](#module\_sonarqube) | ./oidc-client    | n/a     |
| <a name="module_workloads"></a> [workloads](#module\_workloads) | ./vault-workload | n/a     |

## Resources

| Name                                                                                                                                                                  | Type        |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| [random_password.atlantis_password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password)                                          | resource    |
| [random_password.grafana_password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password)                                           | resource    |
| [vault_auth_backend.k8s](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/auth_backend)                                                  | resource    |
| [vault_auth_backend.userpass](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/auth_backend)                                             | resource    |
| [vault_generic_secret.atlantis_auth_secrets](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                            | resource    |
| [vault_generic_secret.atlantis_secrets](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                                 | resource    |
| [vault_generic_secret.ci_secrets](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                                       | resource    |
| [vault_generic_secret.docker_config](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                                    | resource    |
| [vault_generic_secret.grafana_secrets](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                                  | resource    |
| [vault_generic_secret.registry_auth](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                                    | resource    |
| [vault_identity_group.admins](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_group)                                           | resource    |
| [vault_identity_group.developers](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_group)                                       | resource    |
| [vault_identity_oidc_key.key](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_key)                                        | resource    |
| [vault_identity_oidc_provider.cgdevx](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_provider)                           | resource    |
| [vault_identity_oidc_scope.email_scope](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_scope)                            | resource    |
| [vault_identity_oidc_scope.group_scope](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_scope)                            | resource    |
| [vault_identity_oidc_scope.profile_scope](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_scope)                          | resource    |
| [vault_identity_oidc_scope.user_scope](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_scope)                             | resource    |
| [vault_kubernetes_auth_backend_config.k8s](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/kubernetes_auth_backend_config)              | resource    |
| [vault_kubernetes_auth_backend_role.k8s_atlantis](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/kubernetes_auth_backend_role)         | resource    |
| [vault_kubernetes_auth_backend_role.k8s_external_secrets](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/kubernetes_auth_backend_role) | resource    |
| [vault_mount.secret](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/mount)                                                             | resource    |
| [vault_mount.users](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/mount)                                                              | resource    |
| [vault_mount.workloads](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/mount)                                                          | resource    |
| [vault_policy.admin](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy)                                                            | resource    |
| [vault_policy.developer](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy)                                                        | resource    |
| [aws_eks_cluster.cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/eks_cluster)                                                 | data source |
| [aws_eks_cluster_auth.cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/eks_cluster_auth)                                       | data source |

## Inputs

| Name                                                                                                                         | Description                    | Type                                                                                          | Default | Required |
|------------------------------------------------------------------------------------------------------------------------------|--------------------------------|-----------------------------------------------------------------------------------------------|---------|:--------:|
| <a name="input_atlantis_repo_webhook_secret"></a> [atlantis\_repo\_webhook\_secret](#input\_atlantis\_repo\_webhook\_secret) | atlantis webhook secret        | `string`                                                                                      | `""`    |    no    |
| <a name="input_atlantis_repo_webhook_url"></a> [atlantis\_repo\_webhook\_url](#input\_atlantis\_repo\_webhook\_url)          | atlantis webhook url           | `string`                                                                                      | `""`    |    no    |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name)                                                     | primary cluster name           | `string`                                                                                      | `""`    |    no    |
| <a name="input_vault_token"></a> [vault\_token](#input\_vault\_token)                                                        | vault token                    | `string`                                                                                      | `""`    |    no    |
| <a name="input_vcs_bot_ssh_private_key"></a> [vcs\_bot\_ssh\_private\_key](#input\_vcs\_bot\_ssh\_private\_key)              | private key for git operations | `string`                                                                                      | `""`    |    no    |
| <a name="input_vcs_bot_ssh_public_key"></a> [vcs\_bot\_ssh\_public\_key](#input\_vcs\_bot\_ssh\_public\_key)                 | public key for git operations  | `string`                                                                                      | `""`    |    no    |
| <a name="input_vcs_token"></a> [vcs\_token](#input\_vcs\_token)                                                              | token for git operations       | `string`                                                                                      | `""`    |    no    |
| <a name="input_workloads"></a> [workloads](#input\_workloads)                                                                | workloads vault configuration  | <pre>map(object({<br>    description                  = optional(string, "")<br>    }))</pre> | `{}`    |    no    |

## Outputs

No outputs.
<!-- END_TF_DOCS -->