# Users Management

This is a platform Users Management Infrastructure as Code (IaC) main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

### Users Management

#### Input

```terraform
users = {
  # User definition
  "john_doe" = {
    # User's Git username
    vcs_username         = "john_doe_git"
    # User's email
    email                = "john.doe@acme.inc"
    # User's first name
    first_name           = "John"
    # User's Git last name
    last_name            = "Doe"
    # Git teams slugs to add users to
    vcs_team_slugs       = ["${local.gitops_repo_name}-admins"]
    # Access Control List policies
    acl_policies         = ["admin", "default"]
    # OIDC groups
    oidc_groups_for_user = ["admins"]
  }
}
```

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
