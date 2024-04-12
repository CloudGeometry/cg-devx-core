# VCS & OIDC user entities configuration module

This configuration module is designed to hide the complexity associated with user management.

CGDevX is designed to use this module internally, but you can use it directly to a Hashicorp Vault server.

Set the `VAULT_ADDR`, `VAULT_TOKEN`, `GITLAB_OWNER`, and `GITLAB_TOKEN` environment variables as shown in an example
below:

```
export VAULT_ADDR="https://vault.vault.svc.cluster.local:8200"
export VAULT_TOKEN="REPLACE_ME_WITH_VAULT_TOKEN"
export GITLAB_OWNER="YourGitlabOrgHere"
export GITLAB_TOKEN="YourVCSToken"

```

For more details, please see submodule's variables [here](TERRAFORM-README.md)
