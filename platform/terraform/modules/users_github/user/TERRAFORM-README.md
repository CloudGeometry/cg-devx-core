<!-- BEGIN_TF_DOCS -->

## Requirements

No requirements.

## Providers

| Name                                                       | Version |
|------------------------------------------------------------|---------|
| <a name="provider_github"></a> [github](#provider\_github) | n/a     |
| <a name="provider_random"></a> [random](#provider\_random) | n/a     |
| <a name="provider_vault"></a> [vault](#provider\_vault)    | n/a     |

## Modules

No modules.

## Resources

| Name                                                                                                                                     | Type     |
|------------------------------------------------------------------------------------------------------------------------------------------|----------|
| [github_team_membership.team_membership](https://registry.terraform.io/providers/hashicorp/github/latest/docs/resources/team_membership) | resource |
| [random_password.password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password)                      | resource |
| [vault_generic_endpoint.user](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_endpoint)            | resource |
| [vault_generic_secret.user](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/generic_secret)                | resource |
| [vault_identity_entity.user](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_entity)              | resource |
| [vault_identity_entity_alias.user](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_entity_alias)  | resource |

## Inputs

| Name                                                                                                 | Description                                                             | Type           | Default | Required |
|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|----------------|---------|:--------:|
| <a name="input_acl_policies"></a> [acl\_policies](#input\_acl\_policies)                             | n/a                                                                     | `list(string)` | n/a     |   yes    |
| <a name="input_email"></a> [email](#input\_email)                                                    | n/a                                                                     | `string`       | n/a     |   yes    |
| <a name="input_first_name"></a> [first\_name](#input\_first\_name)                                   | n/a                                                                     | `string`       | n/a     |   yes    |
| <a name="input_github_team_slugs"></a> [github\_team\_slugs](#input\_github\_team\_slugs)            | the github team slugs to place the user                                 | `list(string)` | `[]`    |    no    |
| <a name="input_github_username"></a> [github\_username](#input\_github\_username)                    | n/a                                                                     | `string`       | n/a     |   yes    |
| <a name="input_last_name"></a> [last\_name](#input\_last\_name)                                      | n/a                                                                     | `string`       | n/a     |   yes    |
| <a name="input_oidc_groups_for_user"></a> [oidc\_groups\_for\_user](#input\_oidc\_groups\_for\_user) | n/a                                                                     | `list(string)` | n/a     |   yes    |
| <a name="input_user_disabled"></a> [user\_disabled](#input\_user\_disabled)                          | n/a                                                                     | `bool`         | `false` |    no    |
| <a name="input_username"></a> [username](#input\_username)                                           | a distinct username that is unique to this user throughout the platform | `string`       | n/a     |   yes    |
| <a name="input_userpass_accessor"></a> [userpass\_accessor](#input\_userpass\_accessor)              | n/a                                                                     | `string`       | n/a     |   yes    |

## Outputs

| Name                                                                                                               | Description |
|--------------------------------------------------------------------------------------------------------------------|-------------|
| <a name="output_vault_identity_entity_id"></a> [vault\_identity\_entity\_id](#output\_vault\_identity\_entity\_id) | n/a         |

<!-- END_TF_DOCS -->