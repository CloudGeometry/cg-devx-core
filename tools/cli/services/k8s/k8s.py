import base64

from kubernetes import client, watch, config
from kubernetes.client import ApiException

from common.const.common_path import LOCAL_FOLDER
from common.logging_config import logger
from common.retry_decorator import exponential_backoff
from common.tracing_decorator import trace


def write_ca_cert(ca_cert_data):
    ca_cert_path = LOCAL_FOLDER / "k8s_ca.crt"
    with open(ca_cert_path, "wb") as ca_file:
        ca_file.write(base64.b64decode(ca_cert_data))

    return str(ca_cert_path)


class KubeClient:
    def __init__(self, *args, **kwargs):
        self._configuration = client.Configuration()
        if "config_file" in kwargs:
            config.load_kube_config(config_file=kwargs["config_file"], client_configuration=self._configuration)
        if "ca_cert_path" in kwargs:
            self._configuration.ssl_ca_cert = kwargs["ca_cert_path"]
        if "api_key" in kwargs:
            self._configuration.api_key['authorization'] = kwargs["api_key"]
            self._configuration.api_key_prefix['authorization'] = 'Bearer'
        if "endpoint" in kwargs:
            self._configuration.host = kwargs["endpoint"]

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
    def create_custom_object(self, namespace: str, custom_obj: dict, group: str, version: str, plural: str):
        """
        Creates a custom object.
        """
        try:
            custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))

            res = custom_v1_instance.create_namespaced_custom_object(group=group, version=version,
                                                                     namespace=namespace,
                                                                     plural=plural,
                                                                     body=custom_obj)

            return res
        except ApiException as e:
            raise e

    @trace()
    def patch_custom_object(self, namespace: str, name: str, patch, group: str, version: str, plural: str):
        """
        Patch custom object.
        """
        try:
            api_client = client.ApiClient(self._configuration)
            # need to explicitly set headers
            api_client.set_default_header('Content-Type',
                                          api_client.select_header_content_type(['application/json-patch+json']))
            custom_v1_instance = client.CustomObjectsApi(api_client)
            res = custom_v1_instance.patch_namespaced_custom_object(group=group, version=version,
                                                                    namespace=namespace,
                                                                    name=name,
                                                                    plural=plural,
                                                                    body=patch)
            return res
        except ApiException as e:
            raise e

    @trace()
    def remove_custom_object(self, namespace: str, name: str, group: str, version: str, plurals: str):
        """
        Remove custom object.
        """
        try:
            custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))
            res = custom_v1_instance.delete_namespaced_custom_object(group=group, version=version,
                                                                     namespace=namespace,
                                                                     name=name,
                                                                     plural=plurals)
            return res
        except ApiException as e:
            raise e

    @trace()
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

    @trace()
    @exponential_backoff()
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

    @trace()
    @exponential_backoff()
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

    @trace()
    @exponential_backoff()
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

    @trace()
    @exponential_backoff()
    def get_ingress(self, namespace: str, name: str):
        """
        Reads an Ingress.
        """
        network_v1_instance = client.NetworkingV1Api(client.ApiClient(self._configuration))

        try:
            res = network_v1_instance.read_namespaced_ingress(name=name, namespace=namespace)
            return res
        except ApiException as e:
            raise e

    @trace()
    @exponential_backoff()
    def get_certificate(self, namespace: str, name: str):
        """
        Reads a cert-manager certificate.
        """
        return self._get_custom_object(namespace, name, "cert-manager.io", "v1", "certificates")

    def _get_custom_object(self, namespace: str, name: str, group: str, version: str, plurals: str):
        """
        Reads a custom object.
        """
        custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))

        try:
            res = custom_v1_instance.get_namespaced_custom_object(name=name, namespace=namespace, group=group,
                                                                  version=version, plural=plurals)
            return res
        except ApiException as e:
            raise e

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
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

    @trace()
    def wait_for_ingress(self, ingress, timeout: int = 300):
        name = ingress.metadata.name
        namespace = ingress.metadata.namespace

        network_v1_instance = client.NetworkingV1Api(client.ApiClient(self._configuration))

        w = watch.Watch()
        try:
            for event in w.stream(func=network_v1_instance.list_namespaced_ingress,
                                  namespace=namespace,
                                  field_selector=f'metadata.name={name}',
                                  timeout_seconds=timeout):
                if event["object"].status.load_balancer.ingress:
                    w.stop()
                    return True
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Ingress was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", name)

        except ApiException as e:
            raise e

    @trace()
    def wait_for_certificate(self, cert_obj, timeout: int = 300):
        return self.wait_for_custom_object(cert_obj, "cert-manager.io", "v1", "certificates", timeout=timeout)

    @trace()
    def wait_for_custom_object(self, cust_object, group: str, version: str, plurals: str, timeout: int = 300):
        object_name = cust_object["metadata"]["name"]
        namespace = cust_object["metadata"]["namespace"]

        custom_v1_instance = client.CustomObjectsApi(client.ApiClient(self._configuration))
        w = watch.Watch()

        try:
            for event in w.stream(func=custom_v1_instance.list_namespaced_custom_object,
                                  namespace=namespace,
                                  group=group,
                                  version=version,
                                  plural=plurals,
                                  timeout_seconds=timeout):
                if event["object"]["status"]["conditions"][0]["reason"] == "Ready":
                    w.stop()
                    return
                # event.type: ADDED, MODIFIED, DELETED
                if event["type"] == "DELETED":
                    # Custom Object was deleted while waiting for it to start
                    raise Exception("%s deleted before it started", object_name)

        except ApiException as e:
            raise e

    @trace()
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

    @trace()
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

    @trace()
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

    @exponential_backoff()
    @trace()
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
