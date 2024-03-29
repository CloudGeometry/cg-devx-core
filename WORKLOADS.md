# Workloads Quickstart Guide

**Workload** is a high-level abstraction describing application(s) and/or service(s) that provides business value.
Workload is self-contained.

Workloads are configured under CG DevX installation GitOps repository, and then managed by the team owning the Workload.

CG DevX goal is
to provide isolation on Workload level through all the core services provided by CG DevX platform<sup>*</sup>.

> <sup>*</sup> Experimental functions are provided for you to try, but are not documented or supported, and are likely
> to
> be buggy, or to change after release.

## Prerequisites

- Up and running CG DevX cluster.
  Workloads are defined in CG DevX platform GitOps repository.
  All the operations with workloads should be done from the same machine used CG DevX cluster provisioning,
  as there is a hard dependency on the output of CG DevX setup flow.

- There should be no other ongoing changes (active PRs) in CG DevX platform GitOps repository. This is required to avoid
  inconsistency in infrastructure state.

## Workloads management

### Create

Workload configuration is generated by `workload create` [command](tools/cli/commands/workload/README.md#create).
This will create a new feature branch in CG DevX platform GitOps repository,
push all the required configurations, and open a pull request (PR).

You as a user should review a PR and apply the changes via PR automation solution
([Atlantis](https://www.runatlantis.io/)).
You could get more details on Atlantis commands [here](https://www.runatlantis.io/docs/using-atlantis.html).

This will create new repositories for your Workload under your Git organizations.
By default, CG DevX will create two repositories,
one for Workload application(s)/service(s) source code,
and another for manifests + environment definitions, and Infrastructure as Code (IaC).
This is done to provide better isolation and access control,
and could be changed by updating Workload configuration for VCS module.
For instance, you may want to use one repo per application(s)/service(s)
instead of using monorepo that is CG DevX default behavior.

You could delete Workload by running `workload delete` [command](tools/cli/commands/workload/README.md#delete).
This will reverse the changes done by `workload create` command, and open a PR to apply them.

> **Note!**: You must create and delete workloads on by one to avoid conflicts.

### Bootstrap

When PR opened by `workload create` command is merged and closed,
you could bootstrap Workload repositories
with `workload bootstrap` [command](tools/cli/commands/workload/README.md#bootstrap)
This will provide the following features based on templates created by CG DevX team:

- pre-defined folder structure
- environments definition (dev, sta, prod environments)
- IaC templates
- CI/CD process for Workload application(s)/service(s)
- IaC PR automation configuration

> **Note!**: Reference implementation of delivery pipelines, repository structure,
> manifest and environments definitions are given as example of platform capabilities.
> They should and must be adjusted for your specific use case before production use.

The following templates are used by default:

- Workload template [repository](https://github.com/CloudGeometry/cg-devx-wl-template)
- Workload GitOps template [repository](https://github.com/CloudGeometry/cg-devx-wl-gitops-template)

After uploading parametrized repo templates, `workload bootstrap` process will create a PR under your Workload GitOps
repository to initialize secrets, and create IAM role for the Workload service.

Your new workload will have a pre-built CI process triggered by a tag applied to workload source code repository.
[Semantic versioning](https://semver.org/) is used.
CI will build an image (images when you have more than one service in your monorepo)
and upload them to the CG DevX image registry ([Harbor](https://goharbor.io/)).
After that,
it will update the image version of Workload service in K8s deployment definitions in Workload GitOps repository
to trigger CD process.
At this point you could promote changes from `dev` environment to other environments
by running promotion action under Workload GitOps repository.
