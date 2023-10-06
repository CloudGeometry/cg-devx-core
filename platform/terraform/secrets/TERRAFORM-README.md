<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.47 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_secrets"></a> [secrets](#module\_secrets) | ../modules/secrets_vault | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_<GIT_PROVIDER>_token"></a> [<GIT\_PROVIDER>\_token](#input\_<GIT\_PROVIDER>\_token) | n/a | `string` | `"token for git operations"` | no |
| <a name="input_atlantis_repo_webhook_secret"></a> [atlantis\_repo\_webhook\_secret](#input\_atlantis\_repo\_webhook\_secret) | atlantis webhook secret | `string` | `""` | no |
| <a name="input_atlantis_repo_webhook_url"></a> [atlantis\_repo\_webhook\_url](#input\_atlantis\_repo\_webhook\_url) | atlantis webhook url | `string` | `""` | no |
| <a name="input_b64_docker_auth"></a> [b64\_docker\_auth](#input\_b64\_docker\_auth) | container registry auth | `string` | `""` | no |
| <a name="input_vault_token"></a> [vault\_token](#input\_vault\_token) | vault token | `string` | `""` | no |
| <a name="input_vcs_bot_ssh_private_key"></a> [vcs\_bot\_ssh\_private\_key](#input\_vcs\_bot\_ssh\_private\_key) | private key for git operations | `string` | `""` | no |
| <a name="input_vcs_bot_ssh_public_key"></a> [vcs\_bot\_ssh\_public\_key](#input\_vcs\_bot\_ssh\_public\_key) | public key for git operations | `string` | `""` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->