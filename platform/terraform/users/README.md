# Users Management

This is a platform Users Management Infrastructure as Code (IaC) main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

### Users Management

#### Input

```terraform
# Platform GitOps repository name
gitops_repo_name = local.gitops_repo_name
# Git machine user username
bot_vcs_username = local.bot_vcs_username
# Git machine user email
bot_email        = local.bot_email
```

| Name                                                                                                                         | Description                    | Type     | Default | Required |
|------------------------------------------------------------------------------------------------------------------------------|--------------------------------|----------|---------|:--------:|
