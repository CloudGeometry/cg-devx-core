# Platform

This folder serves as a template for user's GitOps repository.
All the files should be templated and will undergo the parametrization process. For more details, please refer
to [templating](TEMPLATING.md).

The **Platform** definition has three main parts

- `/gitops_pipelines`: delivery pipeline configurations. This folder will be added to the user's GitOps repository.
- `/terraform`: Infrastructure as Code & Configuration as Code for all the cloud services, git provider, secrets and
  user management. This folder will be added to the user's GitOps repository.
- `installation-manifests` installation manifests used during setup process. This folder will not be added to the user's
  GitOps repository.
