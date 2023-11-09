<!-- BEGIN_TF_DOCS -->

## Requirements

No requirements.

## Providers

| Name                                                    | Version |
|---------------------------------------------------------|---------|
| <a name="provider_vault"></a> [vault](#provider\_vault) | n/a     |

## Modules

No modules.

## Resources

| Name                                                                                                                            | Type     |
|---------------------------------------------------------------------------------------------------------------------------------|----------|
| [vault_identity_group.admins](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_group)     | resource |
| [vault_identity_group.developers](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_group) | resource |
| [vault_policy.workload-admin](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy)             | resource |
| [vault_policy.workload-developer](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy)         | resource |

## Inputs

| Name                                                                        | Description   | Type     | Default | Required |
|-----------------------------------------------------------------------------|---------------|----------|---------|:--------:|
| <a name="input_workload_name"></a> [workload\_name](#input\_workload\_name) | workload name | `string` | n/a     |   yes    |

## Outputs

No outputs.
<!-- END_TF_DOCS -->