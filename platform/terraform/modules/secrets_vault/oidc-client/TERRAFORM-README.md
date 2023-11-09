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

| Name                                                                                                                                                  | Type        |
|-------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| [vault_generic_secret.creds](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                            | resource    |
| [vault_identity_oidc_assignment.app](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_assignment)          | resource    |
| [vault_identity_oidc_client.app](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_oidc_client)                  | resource    |
| [vault_identity_oidc_client_creds.creds](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/data-sources/identity_oidc_client_creds) | data source |

## Inputs

| Name                                                                                                       | Description                         | Type           | Default | Required |
|------------------------------------------------------------------------------------------------------------|-------------------------------------|----------------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name)                                               | oidc application name               | `string`       | n/a     |   yes    |
| <a name="input_identity_group_ids"></a> [identity\_group\_ids](#input\_identity\_group\_ids)               | list of identity group ids          | `list(string)` | n/a     |   yes    |
| <a name="input_oidc_provider_key_name"></a> [oidc\_provider\_key\_name](#input\_oidc\_provider\_key\_name) | oidc provider key name              | `string`       | n/a     |   yes    |
| <a name="input_redirect_uris"></a> [redirect\_uris](#input\_redirect\_uris)                                | list of redirect urls               | `list(string)` | n/a     |   yes    |
| <a name="input_secret_mount_path"></a> [secret\_mount\_path](#input\_secret\_mount\_path)                  | vault path for stiring oidc secrets | `string`       | n/a     |   yes    |

## Outputs

| Name                                                                                                   | Description |
|--------------------------------------------------------------------------------------------------------|-------------|
| <a name="output_vault_oidc_app_name"></a> [vault\_oidc\_app\_name](#output\_vault\_oidc\_app\_name)    | n/a         |
| <a name="output_vault_oidc_client_id"></a> [vault\_oidc\_client\_id](#output\_vault\_oidc\_client\_id) | n/a         |

<!-- END_TF_DOCS -->