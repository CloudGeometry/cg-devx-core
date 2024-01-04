# CG DevX CLI Workload Management commands

Below is a list of Workload Management commands supported by CG DevX CLI tool.
Workload Management commands depend on local cluster metadata and:
a) could only be executed when CG DevX cluster is already provisioned;
b) should be executed from the same machine as cluster provisioning.

For more details on cluster provisioning, please check [setup command documentation](../README.md#setup)

## Create

Generates declarative configuration of resources required for workload to function. Configuration is placed in the
platform
GitOps repository. CLI automatically pushes changes to feature branch and creates a Pull Request (PR). Changes
introduced with PR should be reviewed and adjusted when necessary.
All the changes to platform GitOps repository should be applied via Atlantis by typing `atlantis apply` in the PR
comments section.

`workload create` command creates:

- Configuration for **VCS** module to create Workload source code monorepo and Workload GitOps repo;
- Configuration for **Secrets** module to create Workload secrets namespace and RBAC;
- Configuration for **Core Services** module to create Image Registry, Code Quality, etc. projects for Workload;
- ArgoCD dedicated Workload Project AppSet to automatically deliver Workload services.

`workload create` command could be executed using arguments, or environment variables.

**Arguments**:

| Name (short, full)                        | Type                                    | Description                                       |
|-------------------------------------------|-----------------------------------------|---------------------------------------------------|
| -wl, --workload-name                      | TEXT                                    | Workload name                                     |
| -wlrn, --workload-repository-name         | TEXT                                    | Name for Workload repository                      |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Name for Workload GitOps repository               |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Set the logging verbosity level, default CRITICAL |

> **Note!**: For all names use kebab-case.

**Command snippet**

Using command arguments

```bash
cgdevxcli workload create --workload-name your-workload-name \ 
                          --workload-repository-name your-workload-repository-name
                          --workload-gitops-repository-name your-workload-gitops-repository-name
```

## Bootstrap

Creates folder structure and injects all the necessary configurations for your Workload into repositories created
by [create command](#create).

By default, bootstrap command uses:

- CG DevX Workload template [repository](https://github.com/CloudGeometry/cg-devx-wl-template)
- CG DevX Workload GitOps template [repository](https://github.com/CloudGeometry/cg-devx-wl-gitops-template)

Those templates provide you:

- Workload repository structure
- Pre-defined Docker file
- CI process
- CD process
- Release promotion process
- GitOps style environment definition
- IaC for out of the cluster cloud resources

You could fork and customize existing template repositories and use them by providing custom template repository URLs
and branches.

> **Note!**: Boostrap command must be executed using the same workload and workload repository names.

`workload bootstrap` command could be executed using arguments, or environment variables.

**Arguments**:

| Name (short, full)                        | Type                                    | Description                                       |
|-------------------------------------------|-----------------------------------------|---------------------------------------------------|
| -wl, --workload-name                      | TEXT                                    | Workload name                                     |
| -wlrn, --workload-repository-name         | TEXT                                    | Name for Workload repository                      |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Name for Workload GitOps repository               |
| -wltu, --workload-template-url            | TEXT                                    | Workload repository template                      |
| -wltb, --workload-template-branch         | TEXT                                    | Workload repository template branch               |
| -wlgu, --workload-gitops-template-url     | TEXT                                    | Workload GitOps repository template               |
| -wlgb, --workload-gitops-template-branch  | TEXT                                    | Workload GitOps repository template branch        |
| -wls, --workload-service-name             | TEXT                                    | Workload service name                             |
| -wlsp, --workload-service-port            | NUMBER                                  | Workload service port, default 3000               |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Set the logging verbosity level, default CRITICAL |

> **Note!**: For all names use kebab-case.

**Command snippet**

Using command arguments

```bash
cgdevxcli workload bootstrap --workload-name your-workload-name \ 
                          --workload-repository-name your-workload-repository-name
                          --workload-gitops-repository-name your-workload-gitops-repository-name
                          --workload-service-name your-first-service-name
                          --workload-service-port your-first-service-name-port
```

## Delete

Removes declarative configuration of resources required for workload to function. CLI automatically pushes changes to
feature branch and creates a Pull Request (PR). Changes introduced with PR should be reviewed and adjusted when
necessary.
All the changes to platform GitOps repository should be applied via Atlantis by typing `atlantis apply` in the PR
comments section.

`workload delete` command deletes all the configuration generated by `workload create` [command](#create):

When executed with `--destroy-resources` flag it will also destroy all the resources created for a specific workload.
Please note that workload GitOps repository name should match one for workload.
When executing with `--destroy-resources` flag enabled it **must** be executed by cluster owner.
Under the hood, it will execute tf destroy locally, and tf state storage is protected and accessible only by the owner. 


> **NOTE!**: this process is irreversible

`workload delete` command could be executed using arguments, or environment variables.

**Arguments**:

| Name (short, full)                        | Type                                    | Description                                       |
|-------------------------------------------|-----------------------------------------|---------------------------------------------------|
| -wl, --workload-name                      | TEXT                                    | Workload name                                     |
| -wldr, --destroy-resources                | Flag                                    | Destroy workload resources                        |
| -wlgrn, --workload-gitops-repository-name | TEXT                                    | Name for Workload GitOps repository               |
| --verbosity                               | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Set the logging verbosity level, default CRITICAL |

> **Note!**: For all names use kebab-case.

**Command snippet**

Using command arguments

```bash
cgdevxcli workload delete --workload-name your-workload-name
```

