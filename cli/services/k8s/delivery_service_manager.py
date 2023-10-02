from cli.common.const.const import ARGOCD_REGISTRY_APP_PATH
from cli.common.const.namespaces import ARGOCD_NAMESPACE
from cli.services.k8s.k8s import KubeClient


class DeliveryServiceManager:
    def __init__(self, k8s_client: KubeClient, argocd_namespace: str = ARGOCD_NAMESPACE):
        self.k8s_client = k8s_client
        self._group = "argoproj.io"
        self._version = "v1alpha1"
        self._namespace = argocd_namespace

    def _create_argocd_object(self, argocd_namespace, argo_obj, plurals):
        return self.k8s_client.create_custom_object(argocd_namespace, argo_obj, self._group, self._version, plurals)

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
                "description": "CGDevX platform core services",
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

        return self._create_argocd_object(self._namespace, argo_proj_cr, "appprojects")

    def create_core_application(self, project_name: str, repo_url: str):
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
                    "targetRevision": "HEAD",
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
                            "factor": 0,
                            "maxDuration": "5m0s",
                        },
                    },
                },
            },
        }

        return self._create_argocd_object(self._namespace, argo_app_cr, "applications")
