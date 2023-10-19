# Git Management

This is a platform Version Control System Management Infrastructure as Code (IaC) main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

### Git Management

#### Input

```terraform
# Platform GitOps repository name
gitops_repo_name             = local.gitops_repo_name
# IaC PR automation webhook URL
atlantis_url                 = local.atlantis_url
# IaC PR automation webhook secret
atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
# Git machine user SSH public key
vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key
```

| Name                                                                                                                         | Description | Type     | Default | Required |
|------------------------------------------------------------------------------------------------------------------------------|-------------|----------|---------|:--------:|
| <a name="input_atlantis_repo_webhook_secret"></a> [atlantis\_repo\_webhook\_secret](#input\_atlantis\_repo\_webhook\_secret) | n/a         | `string` | `""`    |    no    |
| <a name="input_vcs_bot_ssh_public_key"></a> [vcs\_bot\_ssh\_public\_key](#input\_vcs\_bot\_ssh\_public\_key)                 | n/a         | `string` | `""`    |    no    |

#### Output

| Name                                                                                                                    | Description |
|-------------------------------------------------------------------------------------------------------------------------|-------------|
| <a name="output_gitops_repo_git_clone_url"></a> [gitops\_repo\_git\_clone\_url](#output\_gitops\_repo\_git\_clone\_url) | n/a         |
| <a name="output_gitops_repo_html_url"></a> [gitops\_repo\_html\_url](#output\_gitops\_repo\_html\_url)                  | n/a         |
| <a name="output_gitops_repo_ssh_clone_url"></a> [gitops\_repo\_ssh\_clone\_url](#output\_gitops\_repo\_ssh\_clone\_url) | n/a         |
