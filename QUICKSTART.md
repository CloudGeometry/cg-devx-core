# Quickstart guide

## Supported Platforms

This guide outlines the platforms supported by our software, detailing the operating systems and cloud environments that
you can use for running the application and development. Whether you are setting up a development environment or
deploying the application in production, the following platforms are currently supported or will be in future releases.

### Operating Systems

- Linux - Supported
- Mac (ARM) - Supported
- Mac (Intel) - Supported
- Windows - Will be added to a future release

### Git Providers

- GitHub - Supported
- GitLab - Will be added to a future release
- Bitbucket - Will be added to a future release

### Cloud Providers

- AWS - Supported
- Azure - Supported
- GCP - Supported

## Prerequisites

Before you begin the installation process, ensure you have the following prerequisites covered:

### GitHub Setup Requirements

You should have:

1. A user account for the Git platform you're working with. This account will be used to create and manage repositories,
   make commits, manage users, and perform other tasks, such as executing Terraform scripts. For Github, you can create
   one
   following [this guide](https://docs.github.com/en/get-started/signing-up-for-github/signing-up-for-a-new-github-account)
   to sign up for a GitHub account.
3. A GitHub Organization. Organizations are used to group repositories, and CGDevX will create a new repo within a
   specific
   organization so that it's easy to find and manage later should you decide to stop using CGDevX. you don't have one,
   please
   follow [this guide](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch)
   to create a new organization from scratch.
   to create one. The user from step 1 should be part of this organization.
5. A personal access token for the account from step 1. This token will enable CGDevX to take action on the user's
   behalf,
   creating and managing repos, and so on. To get a personal access token, also known as a "developer token", please
   follow the steps as described
   in [this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
   to managing personal access tokens.

   The GitHub token will be used to authenticate with the GitHub API and perform various actions such as creating and
   deleting repositories, groups, and other users. To provide permission for these actions, make sure you select the
   following set of scopes:

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

### Cloud account

#### AWS deployment

Before deploying to AWS, ensure that you have:

1. An AWS account with billing enabled. (Remember, deploying clusters will incur charges. Make sure to destroy
   resources when you're finished with them!)
2. A public hosted zone with DNS routing.
   To set this up,
   you can follow [this guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/AboutHZWorkingWith.html).
3. A user account with `AdministratorAccess`. We recommend that rather than using your root account, you set up a
   new IAM user, then grant it AdministratorAccess. You can
   use [this guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started.html)
   to set up an IAM account,
   and [this guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html) to grant it
   `AdministratorAccess`.
4. The security credentials for this account, which enables CGDevX to use it.
   Use [this guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html#access-keys-and-secret-access-keys)
   to
   get your access keys.
5. The AWS CLI installed and configured to use this user.
   You can use [this guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to install
   the CLI.

#### Azure deployment

Before deploying to Azure, ensure that you have:

1. An Azure account with billing enabled. Subscription ID will be used
   as cloud-profile during setup. 
   (Remember, deploying clusters will incur charges. Make sure to destroy
   resources when you're finished with them!)
2. A public DNS zone hosted in Azure DNS.
   To set this up,
   you can follow [this guide](https://learn.microsoft.com/en-us/azure/dns/dns-delegate-domain-azure-dns).
3. A user account with `Owner` access.
   You can
   use [this guide](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal-subscription-admin)
   to set it up,
   or [this guide](https://learn.microsoft.com/en-us/azure/role-based-access-control/quickstart-assign-role-user-portal)
   to grant permissions to an existing user.
4. The Azure CLI (**az**) and **[kubelogin](https://aka.ms/aks/kubelogin)** installed and configured to use this user.
   You can
   use [this](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
   and [this](https://azure.github.io/kubelogin/install.html) guides
   to install the CLI.

#### Google Cloud deployment

Before deploying to Google Compute Platform, ensure that you have:

1. An account with billing enabled.
   (Remember, deploying clusters will incur charges. Make sure to destroy
   resources when you're finished with them!)
2. Google Cloud Project you will be deploying to. You could follow
   this [guide]( https://developers.google.com/workspace/guides/create-project) to create one. Project ID will be used
   as cloud-profile during setup.
3. A public DNS zone hosted in Cloud DNS.
   To set this up, you can follow [this guide](https://cloud.google.com/dns/docs/set-up-dns-records-domain-name).
4. A user account with `Owner` permissions.
   You can use [this guide](https://developers.google.com/apps-script/guides/admin/assign-cloud-permissions) to grant
   permissions.
5. The Google Cloud CLI (**gcloud**) and **google-cloud-cli-gke-gcloud-auth-plugin** plugin installed and configured to
   use this user.
   You can use [this](https://cloud.google.com/sdk/docs/install-sdk)
   and [this](https://cloud.google.com/sdk/docs/authorizing) guides to install and configure the CLI.

## Installation process

Once you have the prerequisites installed and configured, you are ready to install the CGDevX CLI.
Follow the instructions in the [CLI tool readme](tools/README.md).

Once installed the CLI,
you should be able to provision a cluster using [`setup`](tools/cli/commands/README.md#setup) command.
You can find the full list of the CLI commands [here](tools/cli/commands/README.md).

Once you have a running cluster, you could create your first workload using this [guide](WORKLOADS.md).

For more details please
see [installation guide](https://cloudgeometry.github.io/cg-devx-docs/operators_guide/installation/quickstart/).
