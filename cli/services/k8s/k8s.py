import base64

from kubernetes import client

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

    def list_pods(self):
        api_v1_instance = client.CoreV1Api(client.ApiClient(self._configuration))

        print("Listing pods with their IPs:")
        ret = api_v1_instance.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
