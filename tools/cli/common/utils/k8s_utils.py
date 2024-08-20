from typing import Optional

import kr8s
from kr8s import NotFoundError
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.client.rest import ApiException

from common.logging_config import logger


def find_pod_by_name_fragment(
        kube_config_path: str, name_fragment: str, namespace: str = "default"
) -> Optional[k8s_client.V1Pod]:
    """
    Retrieves the first pod matching a name fragment within a specified Kubernetes namespace that is in a 'Running'
    state.

    :param kube_config_path: The file path to the Kubernetes configuration file.
    :type kube_config_path: str
    :param name_fragment: Part of the pod's name to search for.
    :type name_fragment: str
    :param namespace: The Kubernetes namespace in which to search for the pod, defaults to "default".
    :type namespace: str
    :return: The first matching pod object if found, otherwise None.
    :rtype: Optional[k8s_client.V1Pod]

    :raises FileNotFoundError: If the Kubernetes configuration file cannot be found.
    :raises ApiException: If the Kubernetes API call fails.

    This function logs the process of loading the Kubernetes configuration, searching for pods, and the result of the
    search.
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


async def get_kr8s_pod_instance_by_name(pod_name: str, kubeconfig: str, namespace: str = "DEFAULT") -> kr8s.objects.Pod:
    """
    Asynchronously retrieves a Kubernetes Pod by its full name from a specified namespace.
    This function will raise an error if the Pod cannot be found.

    :param pod_name: The full name of the Pod to retrieve.
    :type pod_name: str
    :param kubeconfig: The file path to the Kubernetes configuration file.
    :type kubeconfig: str
    :param namespace: The namespace from which to retrieve the Pod, defaults to "DEFAULT".
    :type namespace: str
    :return: The Pod object if found.
    :rtype: kr8s.objects.Pod

    :raises NotFoundError: If no Pod with the specified name is found in the given namespace.

    The function logs attempts to retrieve the Pod, and either logs a success message or raises an error depending on
    the outcome.
    """
    logger.info(f"Attempting to retrieve pod '{pod_name}' from namespace '{namespace}'")
    try:
        _ = await kr8s.asyncio.api(kubeconfig=kubeconfig)
        pod = await kr8s.asyncio.objects.Pod.get(pod_name, namespace=namespace)
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
