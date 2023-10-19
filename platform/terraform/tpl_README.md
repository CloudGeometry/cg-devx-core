# Platform IaC

This is your platform Infrastructure as Code (IaC) main folder.
CG DevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

## Blocks

Platform code is organized using the following independent blocks:

### Cloud Infrastructure

Infrastructure management organised under `hosting_provider` folder.

### Secrets

Global (platform wide) secrets management organised under `secrets` folder.

### Users

User, groups, permissions, and access management organized under `users` folder.

### Version Control System (VCS)

Repository and access management organized under `vcs` folder.

### Modules

All the resources are isolated within "provisioning modules" designed to hide the complexity associated with
provisioning and management of a specific resource(s).
They serve as abstraction layer and hide cloud-specific implementation details from the consumer.


