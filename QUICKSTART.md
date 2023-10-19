# Quickstart guide

## Prerequisites

### GitHub

You should have a

1. Organization. If you don't have one, please
   follow [this](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch)
   guide.
2. Account for a machine user used by platform. You could create one
   following [the guide](https://docs.github.com/en/get-started/signing-up-for-github/signing-up-for-a-new-github-account)
3. Personal access token for an account created in a previous step. Please follow the steps as
   described [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).

   GitHub token will be used to authenticate with the GitHub API and perform various actions such as creating, and
   deleting repository, groups, and other users. The Following set of scopes will be used to provision the CG DevX
   (creating and updating GitHub repositories, updating repository webhook URL, etc.):

    - [x] **repo** Full control of private repositories
        - [x] **repo:status** Access commit status
        - [x] **repo_deployment** Access deployment status
        - [x] **public_repo** Access public repositories
        - [x] **repo:invite** Access repository invitations
        - [x] **security_events** Read and write security events
    - [x] **workflow** Update GitHub Action workflows
    - [x] **write:packages** Upload packages to GitHub Package Registry
        - [x] **read:packages** Download packages from GitHub Package Registry
    - [x] **admin:org** Full control of orgs and teams, read and write org projects
        - [x] **write:org** Read and write org and team membership, read and write org projects
        - [x] **read:org** Read org and team membership, read org projects
        - [x] **manage_runners:org** Manage org runners and runner groups
    - [x] **admin:public_key** Full control of user public keys
        - [x] **write:public_key** Write user public keys
        - [x] **read:public_key** Read user public keys
    - [x] **admin:repo_hook** Full control of repository hooks
        - [x] **write:repo_hook** Write repository hooks
        - [x] **read:repo_hook** Read repository hooks
    - [x] **admin:org_hook** Full control of organization hooks
    - [x] **user** Update ALL user data
        - [x] **read:user** Read ALL user profile data
        - [x] **user:email** Access user email addresses (read-only)
        - [x] **user:follow** Follow and unfollow users
    - [x] **delete_repo** Delete repositories
    - [x] **admin:ssh_signing_key** Full control of public user SSH signing keys
        - [x] **write:ssh_signing_key** Write public user SSH signing keys
        - [x] **read:ssh_signing_key** Read public user SSH signing keys

### AWS

You should have a

1. AWS account with billing enabled
2. Public hosted zone with DNS routing. You could follow the
   guide [here](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/AboutHZWorkingWith.html)
3. User account with AdministratorAccess and
   obtain [security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html#access-keys-and-secret-access-keys)
4. AWS CLI

## Installation process

Follow [CLI tool readme](tools/README.md) to launch CG DevX CLI and use [commands](tools/cli/commands/README.md).

## Platform support

Currently, CG DevX CLI works only on Linux and Mac (both ARM and Intel). Windows support may be added in the future.

### Git provider support

- GitHub - supported
- GitLab - work in progress
- Bitbucket - TBD

### Cloud Provider

- AWS - supported
- Azure - work in progress
- GCP - TBD
