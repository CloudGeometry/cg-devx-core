# Platform

The `GitOps` repository has two main sections

- `/gitops_pipelines`: delivery pipeline configurations
- `/terraform`: infrastructure as code & configuration as code for all the cloud services, git provider, secrets and
  user management

## CG DevX services

The CG DevX services:

| Application    | Namespace  | Description                        | URL (where applicable)                  |
|----------------|------------|------------------------------------|-----------------------------------------|
| Vault          | vault      | Secrets Management                 | https://<SECRET_MANAGER_INGRESS_URL>    |
| Argo CD        | argocd     | GitOps Continuous Delivery         | https://<CD_INGRESS_URL>                |
| Argo Workflows | argo       | Application Continuous Integration | https://<CI_INGRESS_URL>                |
| Atlantis       | atlantis   | Terraform Workflow Automation      | https://<IAC_PR_AUTOMATION_INGRESS_URL> |
| Harbor         | harbor     | Image & Helm Chart Registry        | https://<REGISTRY_INGRESS_URL>          |
| Grafana        | monitoring | Observability                      | https://<GRAFANA_INGRESS_URL>           |
| SonarQube      | sonarqube  | Code Quality                       | https://<CODE_QUALITY_INGRESS_URL>      |
| Backstage      | backstage  | Portal                             | https://<PORTAL_INGRESS_URL>            |
---

## GitOps registry

The argocd configurations in this repo can be found in the [registry directory](./registry). The applications that we
build and release on the CG DevX platform will also be registered here in the development, staging, and production
folders.

The `main` branch's registry directory represents the gitops desired state for all apps registered with kubernetes. Argo
CD will automatically apply your desired state to kubernetes through. You can see the Sync status of all of your apps
in [argo cd](https://argocd.cgdevx-demo.demoapps.click).

## Terraform infrastructure as code

The terraform in this repository can be found in the [terraform directory](./terraform). It has entry points for
management of cloud resources, vault configurations, git provider configurations, and user management.

All of our terraform is automated with a tool called atlantis that integrates with your git pull requests. To see the
terraform entry points and under what circumstance they are triggered, see [atlantis.yaml](./atlantis.yaml).

Any change to a `*.tf` file, even a whitespace change, will trigger its corresponding Atlantis workflow once a pull
request is submitted. Within a minute it will post the plan to the pull request with instruction on how to apply the
plan if approved.