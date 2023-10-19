# Vault entities, groups, policies, secrets, OIDC configuration module

This configuration module is designed to hide the complexity associated with provisioning and management of Hashicorp
Vault server.

CG DevX is designed to use this module internally, but you can use it directly to a Hashicorp Vault server.

Set the `VAULT_ADDR`, `VAULT_TOKEN`, and `AWS_PROFILE`(if you are using a named AWS profile) environment variables as
shown in an example below:

```
export VAULT_ADDR="https://vault.vault.svc.cluster.local:8200"
export VAULT_TOKEN="REPLACE_ME_WITH_VAULT_TOKEN"
export AWS_PROFILE="REPLACE_ME_WITH_PROFILE_NAME"
```

For more details, please see module's variables [here](TERRAFORM-README.md)
