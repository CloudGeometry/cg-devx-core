import base64

from kubernetes import client, watch
from kubernetes.client import ApiException

from common.const.common_path import LOCAL_FOLDER


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
        name = name.lower()

        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
        try:
            res = api_v1_instance.read_namespace(name)
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

        sa_name = sa_name.lower()

        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name=sa_name, namespace=namespace))
        try:
            res = api_v1_instance.read_namespaced_service_account(name=sa_name, namespace=namespace)
            return res
        except ApiException as e:
            # service account doesn't exist
            pass
        res = api_v1_instance.create_namespaced_service_account(namespace=namespace, body=body)
        return res

    def create_cluster_role(self, namespace: str, name: str):
        """
        Creates a cluster role.
        """
        name = name.lower()

        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))

        body = client.V1ClusterRole(metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                                    rules=[client.V1PolicyRule(verbs=["*"], api_groups=["*"], resources=["*"])])
        try:
            res = rbac_v1_instance.read_cluster_role(name)
            return res
        except ApiException as e:
            # role doesn't exist
            pass

        res = rbac_v1_instance.create_cluster_role(body=body)
        return res

    def create_cluster_role_binding(self, namespace: str, name: str, role_name: str):
        """
        Creates a ClusterRoleBinding
        """
        name = name.lower()

        rbac_v1_instance = client.RbacAuthorizationV1Api(client.ApiClient(self._configuration))
        body = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=name, namespace=namespace),
            role_ref=client.V1RoleRef(name=role_name, api_group="rbac.authorization.k8s.io", kind="ClusterRole"),
            subjects=[client.V1Subject(kind="ServiceAccount", name=name, namespace=namespace)]
        )
        try:
            res = rbac_v1_instance.read_cluster_role_binding(name=name)
            return res
        except ApiException as e:
            # cluster role binding doesn't exist
            pass

        res = rbac_v1_instance.create_cluster_role_binding(body=body)
        return res

    def create_custom_object(self, argocd_namespace: str, custom_obj: dict, group: str, version: str, plurals: str):
        """
        Creates a custom object.
        """
        try:
            custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))

            res = custom_v1_instance.create_namespaced_custom_object(group=group, version=version,
                                                                     namespace=argocd_namespace,
                                                                     plural=plurals,
                                                                     body=custom_obj)

            return res
        except ApiException as e:
            raise e

    def create_job(self, namespace: str, job_name: str, body):
        """
        Creates Job.
        """
        batch_v1_instance = client.BatchV1Api(client.ApiClient(self._configuration))

        try:
            res = batch_v1_instance.read_namespaced_job(name=job_name, namespace=namespace)
            if res is not None:
                # job exists, most likely a failed job from previous run, should delete as we are going to recreate it
                batch_v1_instance.delete_namespaced_job(name=job_name, namespace=namespace)

                # wait till job is deleted
                w = watch.Watch()
                for event in w.stream(func=batch_v1_instance.list_namespaced_job,
                                      namespace=namespace,
                                      field_selector=f'metadata.name={job_name}',
                                      timeout_seconds=30):
                    # event.type: ADDED, MODIFIED, DELETED
                    if event["type"] == "DELETED":
                        w.stop()
                        break

        except ApiException as e:
            # job doesn't exist
            pass

        res = batch_v1_instance.create_namespaced_job(namespace=namespace, body=body)
        return res

    def get_deployment(self, namespace: str, deployment_name: str):
        """
        Reads a Deployment.
        """
        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))

        try:
            res = apps_v1_instance.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            return res
        except ApiException as e:
            raise e

    def get_pod(self, namespace: str, pod_name: str):
        """
        Reads a Deployment.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        try:
            res = api_v1_instance.read_namespaced_pod(name=pod_name, namespace=namespace)
            return res
        except ApiException as e:
            raise e

    def get_stateful_set_objects(self, namespace: str, name: str):
        """
        Reads a StatefulSet.
        """
        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))

        try:
            res = apps_v1_instance.read_namespaced_stateful_set(name=name, namespace=namespace)
            return res
        except ApiException as e:
            raise e

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

    def wait_for_deployment(self, deployment, timeout: int = 300):
        configured_replicas = deployment.spec.replicas
        name = deployment.metadata.name
        namespace = deployment.metadata.namespace

        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=apps_v1_instance.list_namespaced_deployment,
                                  namespace=namespace,
                                  field_selector=f'metadata.name={name}',
                                  timeout_seconds=timeout):
                if event["object"].status.ready_replicas == configured_replicas:
                    w.stop()
                    return True
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Pod was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", name)

        except ApiException as e:
            raise e

    def wait_for_job(self, job, timeout: int = 300):
        job_name = job.metadata.name
        namespace = job.metadata.namespace

        batch_v1_instance = client.BatchV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=batch_v1_instance.list_namespaced_job,
                                  namespace=namespace,
                                  field_selector=f'metadata.name={job_name}',
                                  timeout_seconds=timeout):
                if bool(event["object"].status.succeeded):
                    w.stop()
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Job was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", job_name)

        except ApiException as e:
            raise e

    def wait_for_pod(self, pod, timeout: int = 300):
        name = pod.metadata.name
        namespace = pod.metadata.namespace

        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=api_v1_instance.list_namespaced_pod,
                                  namespace=namespace,
                                  field_selector=f'metadata.name={name}',
                                  timeout_seconds=timeout):
                if event["object"].status.phase == "Running":
                    w.stop()
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Job was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", name)

        except ApiException as e:
            raise e

    def wait_for_stateful_set(self, stateful_set, timeout: int = 300, wait_availability: bool = True):
        replica_state = "available_replicas"
        if not wait_availability:
            replica_state = "current_replicas"

        configured_replicas = stateful_set.spec.replicas
        name = stateful_set.metadata.name
        namespace = stateful_set.metadata.namespace

        apps_v1_instance = client.AppsV1Api(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=apps_v1_instance.list_namespaced_stateful_set,
                                  namespace=namespace,
                                  field_selector=f'metadata.name={name}',
                                  timeout_seconds=timeout):
                if getattr(event["object"].status, replica_state) == configured_replicas:
                    w.stop()
                    return True
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Set was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", name)

        except ApiException as e:
            raise e

    def create_plain_secret(self, namespace: str, name: str, data: dict, annotations: dict = None,
                            labels: dict = None):
        """
        Creates plain text secret.
        """
        name = name.lower()

        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        body = client.V1Secret(metadata=client.V1ObjectMeta(name=name, namespace=namespace,
                                                            annotations=annotations,
                                                            labels=labels),
                               string_data=data)
        try:
            res = api_v1_instance.read_namespaced_secret(name=name, namespace=namespace)
            return res
        except ApiException as e:
            # service account doesn't exist
            pass

        res = api_v1_instance.create_namespaced_secret(namespace=namespace, body=body)
        return res

    def create_secret(self, namespace: str, name: str, data: dict, annotations: dict = None, labels: dict = None):
        """
        Creates secret.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))
        body = client.V1Secret(metadata=client.V1ObjectMeta(name=name, namespace=namespace,
                                                            annotations=annotations,
                                                            labels=labels),
                               data=data)
        try:
            res = api_v1_instance.read_namespaced_secret(name=name, namespace=namespace)
            return res
        except ApiException as e:
            # service account doesn't exist
            pass

        res = api_v1_instance.create_namespaced_secret(namespace=namespace, body=body)
        return res

    def create_configmap(self, namespace: str, name: str, data: dict, annotations: dict = None, labels: dict = None):
        """
        Creates plain text secret.
        """
        name = name.lower()

        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        body = client.V1ConfigMap(metadata=client.V1ObjectMeta(name=name, namespace=namespace,
                                                               annotations=annotations,
                                                               labels=labels),
                                  data=data
                                  )
        try:
            res = api_v1_instance.read_namespaced_config_map(name=name, namespace=namespace)
            return res
        except ApiException as e:
            # config map doesn't exist
            pass

        res = api_v1_instance.create_namespaced_config_map(namespace=namespace, body=body)
        return res

    def get_secret(self, namespace: str, name: str):
        """
        Get secret.
        """
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        try:
            res = api_v1_instance.read_namespaced_secret(name=name, namespace=namespace)

            # res.metadata.name == "argocd-initial-admin-secret"
            return base64.b64decode(res.data['password']).decode("utf-8")
        except ApiException as e:
            raise e
