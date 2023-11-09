<!-- BEGIN_TF_DOCS -->

## Requirements

| Name                                                             | Version   |
|------------------------------------------------------------------|-----------|
| <a name="requirement_github"></a> [github](#requirement\_github) | ~> 5.17.0 |

## Providers

| Name                                                    | Version |
|---------------------------------------------------------|---------|
| <a name="provider_vault"></a> [vault](#provider\_vault) | n/a     |

## Modules

| Name                                                                    | Source | Version |
|-------------------------------------------------------------------------|--------|---------|
| <a name="module_vault_users"></a> [vault\_users](#module\_vault\_users) | ./user | n/a     |

## Resources

| Name                                                                                                                                                                           | Type        |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| [vault_identity_group_member_entity_ids.oidc_group_membership](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/identity_group_member_entity_ids) | resource    |
| [vault_auth_backend.userpass](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/data-sources/auth_backend)                                                   | data source |
| [vault_identity_group.oidc_identity_groups](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/data-sources/identity_group)                                   | data source |

## Inputs

| Name                                                                  | Description                | Type                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Default                                                    | Required |
|-----------------------------------------------------------------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|:--------:|
| <a name="input_oidc_groups"></a> [oidc\_groups](#input\_oidc\_groups) | vault groups configuration | <pre>map(object({<br>    description = optional(string, "")<br>  }))</pre>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | <pre>{<br>  "admins": {},<br>  "developers": {}<br>}</pre> |    no    |
| <a name="input_users"></a> [users](#input\_users)                     | vault users                | <pre>map(object({<br>    user_disabled                = optional(bool, false)<br>    vcs_username              = optional(string, "")<br>    email                        = optional(string, "")<br>    first_name                   = optional(string, "")<br>    last_name                    = optional(string, "")<br>    vcs_team_slugs            = optional(list(string), [])<br>    acl_policies                 = optional(list(string), ["admin", "default"])<br>    oidc_groups_for_user         = optional(list(string), ["developers"])<br>  }))</pre> | `{}`                                                       |    no    |

## Outputs

No outputs.
<!-- END_TF_DOCS -->