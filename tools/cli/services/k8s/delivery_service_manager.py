import json
from typing import Optional

import httpx
from kubernetes import client
from kubernetes import client as k8s_client

from common.const.const import ARGOCD_REGISTRY_APP_PATH, GITOPS_REPOSITORY_URL
from common.const.namespaces import ARGOCD_NAMESPACE
from common.retry_decorator import exponential_backoff
from common.utils.k8s_utils import get_kr8s_pod_instance_by_name
from services.k8s.k8s import KubeClient


async def get_argocd_token_via_k8s_portforward(
        user: str,
        password: str,
        k8s_pod: k8s_client.V1Pod,
        kube_config_path: str,
        remote_port: int = 8080,
        local_port: int = 8080
) -> Optional[str]:
    """
    Asynchronously retrieves an ArgoCD authentication token by setting up port forwarding from a Kubernetes pod's port
    to a local port.

    :param user: The username for ArgoCD authentication.
    :type user: str
    :param password: The password for ArgoCD authentication.
    :type password: str
    :param k8s_pod: The Kubernetes pod object hosting the ArgoCD service that supports port forwarding.
    :type k8s_pod: k8s_client.V1Pod
    :param kube_config_path: Path to the kubeconfig file for Kubernetes cluster authentication and interaction.
    :type kube_config_path: str
    :param remote_port: The remote port on the Kubernetes pod to forward.
    :type remote_port: int
    :param local_port: The local port to map the remote port's forwarding.
    :type local_port: int
    :return: The ArgoCD authentication token if retrieval is successful; otherwise, None.
    :rtype: Optional[str]
    """
    kr8s_pod = await get_kr8s_pod_instance_by_name(
        pod_name=k8s_pod.metadata.name,
        namespace=ARGOCD_NAMESPACE,
        kubeconfig=kube_config_path
    )
    async with kr8s_pod.portforward(remote_port=remote_port, local_port=local_port):
        return await get_argocd_token(user, password, f'localhost:{local_port}')


async def get_argocd_token(user: str, password: str, endpoint: str = "localhost:8080") -> Optional[str]:
    """
    Asynchronously retrieves an ArgoCD authentication token from a specified endpoint using HTTP POST requests.

    :param user: The username for authentication with ArgoCD.
    :type user: str
    :param password: The password for authentication with ArgoCD.
    :type password: str
    :param endpoint: The endpoint URL where the ArgoCD API is available, defaulting to "localhost:8080".
    :type endpoint: str
    :return: The ArgoCD authentication token if the request succeeds and the user is authenticated; otherwise, None.
    :rtype: Optional[str]
    """
    async with httpx.AsyncClient(verify=False) as httpx_client:
        try:
            response = await httpx_client.post(
                f"https://{endpoint}/api/v1/session",
                headers={"Content-Type": "application/json"},
                content=json.dumps({"username": user, "password": password})
            )
            if response.status_code == 404:
                return None
            elif response.is_success:
                return response.json()["token"]
        except httpx.HTTPStatusError as e:
            raise e


async def delete_application_via_k8s_portforward(
        app_name: str,
        user: str,
        password: str,
        k8s_pod: k8s_client.V1Pod,
        kube_config_path: str,
        remote_port: int = 8080,
        local_port: int = 8080
) -> Optional[bool]:
    """
    Asynchronously retrieves an ArgoCD token and deletes an application from the ArgoCD server by
    port forwarding a Kubernetes pod's port to a local port. This method first obtains an authentication
    token by forwarding the ArgoCD API service's port to a local port and then uses this token to
    send a deletion request to the ArgoCD API.

    :param app_name: The name of the application to be deleted.
    :type app_name: str
    :param user: The username used for ArgoCD token retrieval.
    :type user: str
    :param password: The password used for ArgoCD token retrieval.
    :type password: str
    :param k8s_pod: The Kubernetes pod hosting the ArgoCD service that supports port forwarding.
    :type k8s_pod: k8s_client.V1Pod
    :param kube_config_path: Path to the kubeconfig file for Kubernetes cluster authentication.
    :type kube_config_path: str
    :param remote_port: The port on the Kubernetes pod to be forwarded.
    :type remote_port: int
    :param local_port: The local port to which the remote port's forwarding will be mapped.
    :type local_port: int
    :return: True if the application deletion is successful; otherwise, None.
    :rtype: Optional[bool]
    """
    kr8s_pod = await get_kr8s_pod_instance_by_name(
        pod_name=k8s_pod.metadata.name,
        namespace=ARGOCD_NAMESPACE,
        kubeconfig=kube_config_path
    )

    async with kr8s_pod.portforward(remote_port=remote_port, local_port=local_port):
        # Retrieve the ArgoCD token
        token = await get_argocd_token(user, password, f'localhost:{local_port}')
        if not token:
            return None

        # Use the token to request the deletion of the application
        return await delete_application(app_name, token, f'localhost:{local_port}')


@exponential_backoff(base_delay=5)
async def delete_application(app_name: str, token: str, endpoint: str = "localhost:8080") -> Optional[bool]:
    """
    Asynchronously deletes an application from the ArgoCD server via a specified endpoint using a given authentication token.

    :param app_name: The name of the application to delete.
    :type app_name: str
    :param token: The ArgoCD authentication token.
    :type token: str
    :param endpoint: The endpoint URL where the ArgoCD API is accessed, defaulting to "localhost:8080".
    :type endpoint: str
    :return: True if the application was successfully deleted; otherwise, None.
    :rtype: Optional[bool]
    """
    async with httpx.AsyncClient(verify=False) as httpx_client:
        try:
            response = await httpx_client.delete(
                f"https://{endpoint}/api/v1/applications/{app_name}?cascade=true",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            return response.is_success
        except httpx.HTTPStatusError as e:
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
