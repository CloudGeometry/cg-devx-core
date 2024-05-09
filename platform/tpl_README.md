# Platform

The `GitOps` repository has two main sections:

- `/gitops_pipelines`: Contains delivery pipeline configurations.
- `/terraform`: Manages infrastructure as code & configuration as code for all cloud services, git provider, secrets, and user management.

## CG DevX Services

The CG DevX services are detailed in the following table:

| Application    | Namespace  | Description                                      | URL (where applicable)                  |
|----------------|------------|--------------------------------------------------|-----------------------------------------|
| Vault          | vault      | Manages sensitive data and secrets               | https://<SECRET_MANAGER_INGRESS_URL>    |
| Argo CD        | argocd     | Manages deployments through GitOps               | https://<CD_INGRESS_URL>                |
| Argo Workflows | argo       | Supports CI processes for applications           | https://<CI_INGRESS_URL>                |
| Atlantis       | atlantis   | Automates Terraform plans and applies via GitOps | https://<IAC_PR_AUTOMATION_INGRESS_URL> |
| Harbor         | harbor     | Docker registry for images and Helm charts       | https://<REGISTRY_INGRESS_URL>          |
| Grafana        | monitoring | Dashboard for monitoring and observability       | https://<GRAFANA_INGRESS_URL>           |
| SonarQube      | sonarqube  | Analyzes and visualizes code quality             | https://<CODE_QUALITY_INGRESS_URL>      |
| Backstage      | backstage  | Developer portal for technical insights          | https://<PORTAL_INGRESS_URL>            |

For more details on platform usage, please refer to the [Operator Guide](https://cloudgeometry.github.io/cg-devx-docs/operators_guide/concept/), the [Developer Guide](https://cloudgeometry.github.io/cg-devx-docs/developers_guide/concept/), or the [official documentation](https://cloudgeometry.github.io/cg-devx-docs/).

---

## GitOps Registry

ArgoCD configurations in this repository can be found in the [core services directory](./gitops-pipelines/delivery/clusters/cc-cluster/core-services). The applications we build and release on the CG DevX platform are registered here in the development, staging, and production folders.

The `main` branch's registry directory represents the GitOps desired state for all apps registered with Kubernetes. Argo CD automatically applies your desired state to Kubernetes. You can see the Sync status of all your apps in [Argo CD](https://<CD_INGRESS_URL>).

## Terraform Infrastructure as Code

Terraform configurations in this repository are located in the [terraform directory](./terraform). It includes entry points for managing cloud resources, Vault configurations, Git provider configurations, and user management.

All our Terraform operations are automated with Atlantis, which integrates with your Git pull requests. To see the Terraform entry points and under what circumstances they are triggered, review [atlantis.yaml](./atlantis.yaml).

Any change to a `*.tf` file, even a whitespace change, will trigger its corresponding Atlantis workflow once a pull request is submitted. Within a minute, it will post the plan to the pull request with instructions on how to apply the plan if approved.
