# Secrets Management

This is a platform Secrets Management Infrastructure as Code (IaC) main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

### Secrets Management

#### Input

```terraform
# K8s cluster name
cluster_name                 = local.cluster_name
# workloads
workloads                    = local.workloads
# Git machine user SSH public key
vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
# Git machine user SSH private key
vcs_bot_ssh_private_key      = var.vcs_bot_ssh_private_key
# Git access token
vcs_token                    = var.vcs_token
# IaC PR automation webhook secret
atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
# IaC PR automation webhook URL
atlantis_repo_webhook_url    = var.atlantis_repo_webhook_url
#Secrets Manager root access token
vault_token                  = var.vault_token
```

| Name                                                                                                                         | Description                    | Type     | Default | Required |
|------------------------------------------------------------------------------------------------------------------------------|--------------------------------|----------|---------|:--------:|
| <a name="input_atlantis_repo_webhook_secret"></a> [atlantis\_repo\_webhook\_secret](#input\_atlantis\_repo\_webhook\_secret) | atlantis webhook secret        | `string` | `""`    |    no    |
| <a name="input_atlantis_repo_webhook_url"></a> [atlantis\_repo\_webhook\_url](#input\_atlantis\_repo\_webhook\_url)          | atlantis webhook url           | `string` | `""`    |    no    |
| <a name="input_vault_token"></a> [vault\_token](#input\_vault\_token)                                                        | vault token                    | `string` | `""`    |    no    |
| <a name="input_vcs_bot_ssh_private_key"></a> [vcs\_bot\_ssh\_private\_key](#input\_vcs\_bot\_ssh\_private\_key)              | private key for git operations | `string` | `""`    |    no    |
| <a name="input_vcs_bot_ssh_public_key"></a> [vcs\_bot\_ssh\_public\_key](#input\_vcs\_bot\_ssh\_public\_key)                 | public key for git operations  | `string` | `""`    |    no    |
| <a name="input_vcs_token"></a> [vcs\_token](#input\_vcs\_token)                                                              | token for git operations       | `string` | `""`    |    no    |

