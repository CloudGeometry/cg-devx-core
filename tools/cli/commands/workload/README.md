# CG DevX CLI Workload Management Commands

This document provides a detailed guide on the Workload Management commands supported by the CG DevX CLI tool.
These commands require that the CG DevX cluster is already provisioned and should be executed from the same machine used
for cluster provisioning.
For more information on cluster provisioning, please refer to the [setup command documentation](../README.md#setup).

## Create

The `workload create` command generates and configures resources required for the workload. It automatically pushes
changes to a feature branch and creates a pull request (PR) for review and adjustment.
All the changes to platform GitOps repository should be applied via Atlantis by typing `atlantis apply` in the PR
comments section.

**Operations performed:**

- Creates configuration for the VCS module to establish Workload source code and GitOps repositories.
- Sets up the Secrets module for managing Workload secrets and RBAC.
- Configures Core Services like Image Registry and Code Quality projects.
- Initializes an ArgoCD Project AppSet for automated Workload service delivery.

**Usage:** This command can be executed using command-line arguments or environment variables.

### Command Arguments

| Name (short, full)                        | Type                                    | Description                               |
|-------------------------------------------|-----------------------------------------|-------------------------------------------|
| -wl, --workload-name                      | TEXT                                    | Name of the Workload                      |
| -wlrn, --workload-repository-name         | TEXT                                    | Workload repository name                  |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Workload GitOps repository name           |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Logging verbosity level, default CRITICAL |

> **Note:** Use kebab-case for all names.

**Example:**

```bash
cgdevxcli workload create --workload-name your-workload-name \
                          --workload-repository-name your-workload-repository-name \
                          --workload-gitops-repository-name your-workload-gitops-repository-name
```

## Bootstrap

The workload bootstrap command sets up the folder structure and injects necessary configurations into repositories
created by the [create command](#create).

Templates used:

Workload repository: [CG DevX Workload GitOps template](https://github.com/CloudGeometry/cg-devx-wl-gitops-template)
Workload GitOps
repository: [CG DevX Workload GitOps template](https://github.com/CloudGeometry/cg-devx-wl-gitops-template)

These templates provide a predefined Docker file, CI/CD processes, release promotion process, and environment
definitions.

### Customization

You can fork and customize these templates and specify custom URLs and branches during execution.

### Usage

This command can be executed using command-line arguments or environment variables.

> **Note**: Boostrap command must be executed using the same workload and workload repository names.

### Command Arguments:

| Name (short, full)                        | Type                                    | Description                                       |
|-------------------------------------------|-----------------------------------------|---------------------------------------------------|
| -wl, --workload-name                      | TEXT                                    | Workload name                                     |
| -wlrn, --workload-repository-name         | TEXT                                    | Workload repository name                          |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Workload GitOps repository name                   |
| -wltu, --workload-template-url            | TEXT                                    | URL of the workload repository template           |
| -wltb, --workload-template-branch         | TEXT                                    | Branch of the workload repository template        |
| -wlgu, --workload-gitops-template-url     | TEXT                                    | URL of the workload GitOps repository template    |
| -wlgb, --workload-gitops-template-branch  | TEXT                                    | Branch of the workload GitOps repository template |
| -wls, --workload-service-name             | TEXT                                    | Name of the service within the workload           |
| -wlsp, --workload-service-port            | NUMBER                                  | Service port, default 3000                        |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Logging verbosity level, default CRITICAL         |

> **Note**: For all names use kebab-case.

**Example:**

```bash
cgdevxcli workload bootstrap --workload-name your-workload-name \
                             --workload-repository-name your-workload-repository-name \
                             --workload-gitops-repository-name your-workload-gitops-repository-name \
                             --workload-service-name your-first-service-name \
                             --workload-service-port your-first-service-port
```

## Delete

The `workload delete` command removes the declarative configuration of resources required for a workload. It
automatically
pushes changes to a feature branch and creates a pull request for review.

**Important**:

`workload delete` command deletes all the configuration generated by `workload create` [command](#create):
If executed with the `--destroy-resources` flag, it will also destroy all the resources created for the specific
workload. When used with `--destroy-resources` flag enabled it **must** be executed by cluster owner. Under the hood, it
will execute tf destroy locally, and tf state storage is protected and accessible only by the owner.

> **NOTE!**: This operation is **irreversible**.

# Command Arguments:

| Name (short, full)                        | Type                                    | Description                               |
|-------------------------------------------|-----------------------------------------|-------------------------------------------|
| -wl, --workload-names                     | TEXT                                    | Workload name(s), can be multiple         |
| --all                                     | Flag                                    | Flag to destroy all existing workloads    |
| -wldr, --destroy-resources                | Flag                                    | Flag to destroy workload resources        |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Workload GitOps repository name           |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Logging verbosity level, default CRITICAL |

Note: This process is irreversible.

**Command snippet**

Using command arguments

```bash
cgdevxcli workload delete --workload-name your-workload-name
```

