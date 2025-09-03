from common.enums.optional_services import OptionalServices

OPTIONAL_SERVICES_MAP = {
    OptionalServices.GitHub: ["50-actions-runner-controller.yaml", "60-github-runner.yaml"],
    OptionalServices.GitLab: ["60-gitlab-runner.yaml"],
    OptionalServices.NvidiaGpuOperator: ["180-nvidia-gpu-operator.yaml"],
    OptionalServices.KEDA: ["180-keda.yaml"],
    OptionalServices.KubeVirt: ["180-kubevirt.yaml"],
    OptionalServices.VPA: ["180-vpa.yaml"],
    OptionalServices.Perfectscale: ["180-perfectscale.yaml"],
    OptionalServices.ClusterAutoscaler: ["30-cluster-autoscaler.yaml"],
    OptionalServices.Backstage: ["55-oauth2-proxy.yaml", "170-backstage.yaml"]
}


def build_argo_exclude_string(services: [str]) -> str:
    if not services:
        services = []
    oc_to_ignore = OPTIONAL_SERVICES_MAP.copy()
    for svc in services:
        oc_to_ignore.pop(svc)
    if oc_to_ignore:
        return ",".join([x for xs in list(oc_to_ignore.values()) for x in xs])
    else:
        return ""
