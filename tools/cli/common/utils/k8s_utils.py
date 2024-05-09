from typing import Optional

import kr8s
from kr8s import NotFoundError
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.client.rest import ApiException

from common.logging_config import logger
from common.retry_decorator import exponential_backoff


def find_pod_by_name_fragment(
        kube_config_path: str, name_fragment: str, namespace: str = "default"
) -> Optional[k8s_client.V1Pod]:
    """
    Retrieves the first pod matching a name fragment within a specified Kubernetes namespace that is in a 'Running' state.

    Args:
        kube_config_path (str): The file path to the Kubernetes configuration file.
        name_fragment (str): Part of the pod's name to search for.
        namespace (str): The Kubernetes namespace in which to search for the pod.

    Returns:
        k8s_client.V1Pod | None: The first matching pod object if found, otherwise None.

    Raises:
        FileNotFoundError: If the Kubernetes configuration file cannot be found.
        ApiException: If the Kubernetes API call fails.
    """
    try:
        logger.info(f"Loading Kubernetes configuration from {kube_config_path}")
        k8s_config.load_kube_config(kube_config_path)

        v1_api = k8s_client.CoreV1Api()
        logger.info(f"Searching for pods containing '{name_fragment}' in their name in namespace {namespace}")
        pods = v1_api.list_namespaced_pod(namespace, watch=False)

        for pod in pods.items:
            if name_fragment in pod.metadata.name and pod.status.phase == 'Running':
                logger.info(f"Found pod: {pod.metadata.name}")
                return pod
        logger.warning(f"No pod matching the name fragment '{name_fragment}' found in namespace {namespace}")
        return None
    except FileNotFoundError as e:
        logger.error(f"Kubernetes configuration file not found: {e}")
        raise
    except ApiException as e:
        logger.error(f"Failed to connect to Kubernetes API: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


@exponential_backoff(base_delay=5)
def get_kr8s_pod_instance_by_name(pod_name: str, kubeconfig: str, namespace: str = "DEFAULT") -> kr8s.objects.Pod:
    """
    Retrieves a Kubernetes Pod by its full name from a specified namespace. Raises an error if the Pod cannot be found.

    Args:
        pod_name (str): The full name of the Pod to retrieve.
        kubeconfig (str): The file path to the Kubernetes configuration file.
        namespace (str): The namespace from which to retrieve the Pod.

    Returns:
        Pod: The Pod object if found.

    Raises:
        NotFoundError: If no Pod with the specified name is found in the given namespace.
    """
    logger.info(f"Attempting to retrieve pod '{pod_name}' from namespace '{namespace}'")
    try:
        _ = kr8s.api(kubeconfig=kubeconfig)
        pod = kr8s.objects.Pod.get(pod_name, namespace=namespace)
        if not pod:
            logger.error(f"No Pod found with name {pod_name} in namespace {namespace}.")
            raise NotFoundError(f"No Pod found with name {pod_name} in namespace {namespace}.")
        logger.info(f"Pod '{pod_name}' successfully retrieved from namespace '{namespace}'.")
        return pod
    except NotFoundError as e:
        logger.error(f"NotFoundError: {e}")
        raise NotFoundError(f"Failed to retrieve the Pod: {e}")
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise Exception(f"An error occurred while retrieving the Pod: {e}")
