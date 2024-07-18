<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_gitlab"></a> [gitlab](#requirement\_gitlab) | <GITLAB_PROVIDER_VERSION> |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_gitlab"></a> [gitlab](#provider\_gitlab) | <GITLAB_PROVIDER_VERSION> |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_gitops-repo"></a> [gitops-repo](#module\_gitops-repo) | ./repository | n/a |
| <a name="module_workload_repos"></a> [workload\_repos](#module\_workload\_repos) | ./repository | n/a |

## Resources

| Name | Type |
|------|------|
| [gitlab_user_sshkey.vcs-bot](https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs/resources/user_sshkey) | resource |
| [gitlab_group.owner](https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs/data-sources/group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cd_webhook_secret"></a> [cd\_webhook\_secret](#input\_cd\_webhook\_secret) | n/a | `string` | `""` | no |
| <a name="input_cd_webhook_url"></a> [cd\_webhook\_url](#input\_cd\_webhook\_url) | n/a | `string` | `""` | no |
| <a name="input_atlantis_repo_webhook_secret"></a> [atlantis\_repo\_webhook\_secret](#input\_atlantis\_repo\_webhook\_secret) | n/a | `string` | `""` | no |
| <a name="input_atlantis_url"></a> [atlantis\_url](#input\_atlantis\_url) | n/a | `string` | `""` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | n/a | `string` | `""` | no |
| <a name="input_gitops_repo_name"></a> [gitops\_repo\_name](#input\_gitops\_repo\_name) | n/a | `string` | `"gitops"` | no |
| <a name="input_vcs_bot_ssh_public_key"></a> [vcs\_bot\_ssh\_public\_key](#input\_vcs\_bot\_ssh\_public\_key) | n/a | `string` | `""` | no |
| <a name="input_vcs_owner"></a> [vcs\_owner](#input\_vcs\_owner) | n/a | `string` | `""` | no |
| <a name="input_vcs_subscription_plan"></a> [vcs\_subscription\_plan](#input\_vcs\_subscription\_plan) | True for advanced github/gitlab plan. False for free tier | `bool` | `false` | no |
| <a name="input_workloads"></a> [workloads](#input\_workloads) | workloads configuration | <pre>map(object({<br>    description = optional(string, "")<br>    repos = map(object({<br>      description            = optional(string, "")<br>      visibility             = optional(string, "private")<br>      auto_init              = optional(bool, false)<br>      archive_on_destroy     = optional(bool, false)<br>      has_issues             = optional(bool, false)<br>      default_branch_name    = optional(string, "main")<br>      delete_branch_on_merge = optional(bool, true)<br>      branch_protection      = optional(bool, true)<br>      atlantis_enabled       = optional(bool, false)<br>    }))<br>  }))</pre> | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_gitops_repo_git_clone_url"></a> [gitops\_repo\_git\_clone\_url](#output\_gitops\_repo\_git\_clone\_url) | n/a |
| <a name="output_gitops_repo_html_url"></a> [gitops\_repo\_html\_url](#output\_gitops\_repo\_html\_url) | n/a |
| <a name="output_gitops_repo_ssh_clone_url"></a> [gitops\_repo\_ssh\_clone\_url](#output\_gitops\_repo\_ssh\_clone\_url) | n/a |
<!-- END_TF_DOCS -->