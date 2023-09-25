import base64

from kubernetes import client, config, watch
from kubernetes.client import ApiException

from cli.common.const.common_path import LOCAL_FOLDER


def write_ca_cert(ca_cert_data):
    ca_cert_path = LOCAL_FOLDER / "k8s_ca.crt"
    with open(ca_cert_path, "wb") as ca_file:
        ca_file.write(base64.b64decode(ca_cert_data))

    return str(ca_cert_path)


class KubeClient:
    def __init__(self, ca_cert_path, api_key, endpoint):
        self._configuration = client.Configuration()
        self._configuration.ssl_ca_cert = ca_cert_path  # <<< look here>>>
        self._configuration.api_key['authorization'] = api_key
        self._configuration.api_key_prefix['authorization'] = 'Bearer'
        self._configuration.host = endpoint

    def create_namespace(self, name: str):
        """
        Creates a namespace.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
        try:
            res = api_v1_instance.read_namespace("name")
            return res
        except ApiException as e:
            # namespace doesn't exist
            pass
        res = api_v1_instance.create_namespace(body=body)
        return res

    def create_service_account(self, namespace: str, sa_name: str):
        """
        Creates a service account.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name=sa_name, namespace=namespace))
        try:
            res = api_v1_instance.read_namespaced_service_account(name=sa_name, namespace=namespace)
            return res
        except ApiException as e:
            # service account doesn't exist
            res = api_v1_instance.create_namespaced_service_account(body=body)
            return res

    def create_cluster_role(self, namespace: str, name: str):
        """
        Creates a cluster role.
        """
        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))

        body = client.V1ClusterRole(metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                                    rules=client.V1PolicyRule(verbs=["*"], api_groups=["*"], resources=["*"]))
        try:
            res = rbac_v1_instance.create_cluster_role(body=body)
            return res
        except ApiException as e:
            raise e

    def create_cluster_role_binding(self, namespace: str, name: str, r_name: str):
        """
        Creates a ClusterRoleBinding
        """
        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))
        body = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=name, namespace=namespace),
            role_ref=client.V1RoleRef(name=r_name, api_group="rbac.authorization.k8s.io", kind="ClusterRole"),
            subjects=[client.V1Subject(kind="ServiceAccount", name=name, namespace=namespace)]
        )
        try:
            rbac_v1_instance.read_cluster_role_binding(name=name)
        except ApiException as e:
            # cluster role binding doesn't exist
            pass
        res = rbac_v1_instance.create_cluster_role_binding(body=body)
        return res

    def get_deployment(self, namespace: str, deployment_name: str):
        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))

        try:
            deployment = apps_v1_instance.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            return deployment
        except ApiException as e:
            raise e

    def get_stateful_set_objects(self, namespace: str, name: str):
        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))

        try:
            stateful_set = apps_v1_instance.read_namespaced_stateful_set(name=name, namespace=namespace)
            return stateful_set
        except ApiException as e:
            raise e

    def create_argocd_bootstrap_job(self, namespace: str, sa_name: str, image: str, command: [str], envs: dict = None):
        env_vars = None
        if envs is not None:
            env_vars = []
            for k, v in envs.items():
                env_vars.append(client.V1EnvVar(name=k, value=v))

        job_name = "kustomize-apply-argocd"
        volumes = [client.V1Volume(name="ssh-key-secret",
                                   empty_dir=client.V1EmptyDirVolumeSource(medium="Memory"),
                                   secret=client.V1SecretVolumeSource(secret_name="repo-credentials",
                                                                      items=[client.V1KeyToPath(key="sshPrivateKey",
                                                                                                path="id_rsa",
                                                                                                mode=0o600),
                                                                             client.V1KeyToPath(key="sshPublicKey",
                                                                                                path="id_rsa.pub",
                                                                                                mode=0o644)]))]
        body = client.V1Job(metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
                            spec=client.V1JobSpec(template=client.V1PodTemplateSpec(
                                spec=client.V1PodSpec(containers=[
                                    client.V1Container(name="main", image=image,
                                                       command=["/bin/sh", "-c"].extend(command),
                                                       env=env_vars,
                                                       volumes=volumes)],
                                    service_account_name=sa_name, restart_policy="Never")), backoff_limit=1))

        return self.create_job(namespace, job_name, body)

    def create_job(self, namespace: str, job_name: str, body):
        """
        Creates job.
        """
        batch_v1_instance = client.BatchV1Api(client.ApiClient(self._configuration))

        try:
            res = batch_v1_instance.read_namespaced_job(name=job_name, namespace=namespace)
            if res is not None:
                # job exists, most likely a failed job from previous run, should delete as we are going to recreate it
                batch_v1_instance.delete_namespaced_job(name=job_name, namespace=namespace)

        except ApiException as e:
            # job doesn't exist
            pass

        res = batch_v1_instance.create_namespaced_job(namespace=namespace, body=body)
        return res

    def remove_service_account(self, namespace: str, sa_name: str):
        """
        Removes a service account.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        try:
            api_v1_instance.delete_namespaced_service_account(name=sa_name, namespace=namespace)
            return True

        except ApiException as e:
            raise e

    def remove_cluster_role(self, r_name: str):
        """
        Removes a cluster role.
        """
        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))
        try:
            rbac_v1_instance.delete_cluster_role(name=r_name)
            return True

        except ApiException as e:
            raise e

    def remove_cluster_role_binding(self, rb_name: str):
        """
        Removes a cluster role binding.
        """
        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))
        try:
            rbac_v1_instance.delete_cluster_role_binding(name=rb_name)
            return True

        except ApiException as e:
            raise e

    def wait_for_deployment(self, namespace: str, deployment_name: str, timeout: int = 120):
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()
        try:
            for event in w.stream(func=api_v1_instance.list_namespaced_pod,
                                  namespace=namespace,
                                  label_selector=f"name in ({deployment_name})",
                                  timeout_seconds=timeout):
                if event["object"].status.phase == "Running":
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Pod was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", deployment_name)

        except ApiException as e:
            raise e

    def wait_for_job(self, namespace: str, job_name: str, timeout: int = 120):
        batch_v1_instance = client.BatchV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=batch_v1_instance.list_namespaced_job,
                                  namespace=namespace,
                                  label_selector=f"name in ({job_name})",
                                  timeout_seconds=timeout):
                if event["object"].status.phase == "Running":
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Job was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", job_name)

        except ApiException as e:
            raise e

    def wait_for_stateful_set(self, namespace: str, name: str, timeout: int = 120):
        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=apps_v1_instance.list_namespaced_stateful_set,
                                  namespace=namespace,
                                  label_selector=f"name in ({name})",
                                  timeout_seconds=timeout):
                if event["object"].status.phase == "Running":
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Set was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", name)

        except ApiException as e:
            raise e

    def create_secret(self, namespace: str, name: str, data: dict):
        """
        Creates secret.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1Secret(metadata=client.V1ObjectMeta(name=name, namespace=namespace,
                                                            annotations={"managed-by": "argocd.argoproj.io"},
                                                            labels={"argocd.argoproj.io/secret-type": "repository"}),
                               data=data)
        try:
            res = api_v1_instance.read_namespaced_secret(name=name, namespace=namespace)
            return res
        except ApiException as e:
            # service account doesn't exist
            res = api_v1_instance.create_namespaced_secret(namespace=namespace, body=body)
            return res

    def get_secret(self, namespace: str, name: str):
        """
        Get secret.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        try:
            res = api_v1_instance.read_namespaced_secret(name=name, namespace=namespace)

            k = res.metadata.name
            v = base64.b64decode(res.data['password'])
            return k, v
        except ApiException as e:
            raise e

    def create_custom_object(self, argocd_namespace, argo_obj):
        custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))
        try:
            res = custom_v1_instance.create_namespaced_custom_object(
                namespace=argocd_namespace,
                body=argo_obj,
            )
            return res
        except ApiException as e:
            raise e
