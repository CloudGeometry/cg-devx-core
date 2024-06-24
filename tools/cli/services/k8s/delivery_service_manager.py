import json

import requests
from kubernetes import client
from requests import HTTPError

from common.const.const import ARGOCD_REGISTRY_APP_PATH, GITOPS_REPOSITORY_URL
from common.const.namespaces import ARGOCD_NAMESPACE
from common.retry_decorator import exponential_backoff
from services.k8s.k8s import KubeClient


@exponential_backoff(base_delay=5)
def get_argocd_token(user, password, endpoint="localhost:8080"):
    try:
        response = requests.post(f"https://{endpoint}/api/v1/session",
                                 verify=False,
                                 headers={"Content-Type": "application/json"},
                                 data=json.dumps({"username": user, "password": password})
                                 )
        if response.status_code == requests.codes["not_found"]:
            return None
        elif response.ok:
            res = json.loads(response.text)
            return res["token"]
    except HTTPError as e:
        raise e


@exponential_backoff(base_delay=5)
def delete_application(app_name, token, endpoint="localhost:8080"):
    try:
        response = requests.delete(f"https://{endpoint}/api/v1/applications/{app_name}?cascade=true",
                                   verify=False,
                                   headers={
                                       "Content-Type": "application/json",
                                       "Authorization": f"Bearer {token}"
                                   }
                                   )
        if response.ok:
            return
    except HTTPError as e:
        raise e


class DeliveryServiceManager:
    def __init__(self, k8s_client: KubeClient, argocd_namespace: str = ARGOCD_NAMESPACE):
        self._k8s_client = k8s_client
        self._group = "argoproj.io"
        self._version = "v1alpha1"
        self._namespace = argocd_namespace

    def _create_argocd_object(self, argo_obj, plurals):
        return self._k8s_client.create_custom_object(self._namespace, argo_obj, self._group, self._version, plurals)

    def create_project(self, project_name: str, repos=None):
        if repos is None:
            repos = ["*"]
        argo_proj_cr = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "AppProject",
            "metadata": {
                "name": project_name,
                "namespace": self._namespace,
                # Finalizer that ensures that project is not deleted until it is not referenced by any application
                "finalizers": ["resources-finalizer.argocd.argoproj.io"]
            },
            "spec": {
                "description": "CG DevX platform core services",
                # allow manifests only from gitops repo
                "sourceRepos": repos,
                # Only permit applications to deploy in the same cluster
                "destinations": [
                    {
                        "namespace": "*",
                        "name": "*",
                        "server": "*"  # https://kubernetes.default.svc
                    }
                ],
                "clusterResourceWhitelist": [
                    {
                        "group": "*",
                        "kind": "*"
                    }
                ],
                "namespaceResourceWhitelist": [
                    {
                        "group": "*",
                        "kind": "*"
                    }
                ]
            }
        }

        return self._create_argocd_object(argo_proj_cr, "appprojects")

    def create_core_application(self, project_name: str, repo_url: str, exclude: str = ""):
        argo_app_cr = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": "registry",
                "namespace": self._namespace,
                "annotations": {"argocd.argoproj.io/sync-wave": "1"},
            },
            "spec": {
                "source": {
                    "repoURL": repo_url,
                    "path": ARGOCD_REGISTRY_APP_PATH,
                    "targetRevision": "HEAD"
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": self._namespace,
                },
                "project": project_name,
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True,
                    },
                    "syncOptions": ["CreateNamespace=true"],
                    "retry": {
                        "limit": 5,
                        "backoff": {
                            "duration": "5s",
                            "factor": 2,
                            "maxDuration": "5m0s",
                        },
                    },
                },
            },
        }

        if exclude:
            argo_app_cr["spec"]["source"]["directory"] = {"exclude": f"{{{exclude}}}"}

        return self._create_argocd_object(argo_app_cr, "applications")

    def create_argocd_bootstrap_job(self, sa_name: str):
        """
        Creates ArgoCD bootstrap job
        """
        image = "bitnami/kubectl"
        manifest_path = f"{GITOPS_REPOSITORY_URL}/platform/installation-manifests/argocd?ref=main"

        bootstrap_entry_point = ["/bin/sh", "-c", f"kubectl apply -k '{manifest_path}'"]

        job_name = "kustomize-apply-argocd"

        body = client.V1Job(metadata=client.V1ObjectMeta(name=job_name, namespace=self._namespace),
                            spec=client.V1JobSpec(template=client.V1PodTemplateSpec(
                                spec=client.V1PodSpec(
                                    containers=[
                                        client.V1Container(name="main", image=image,
                                                           command=bootstrap_entry_point)],
                                    service_account_name=sa_name,
                                    restart_policy="Never")),
                                backoff_limit=1))

        return self._k8s_client.create_job(self._namespace, job_name, body)

    def turn_off_app_sync(self, name: str):
        sync_policy_patch = [{
            "op": "remove",
            "path": "/spec/syncPolicy",
            "value": ""
        }]
        return self._k8s_client.patch_custom_object(self._namespace, name, sync_policy_patch, self._group,
                                                    self._version, "applications")

    def delete_app(self, name: str):
        return self._k8s_client.remove_custom_object(self._namespace, name, self._group, self._version, "applications")
