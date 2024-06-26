from common.enums.optional_services import OptionalServices

OPTIONAL_SERVICES_MAP = {
    OptionalServices.NvidiaGpuOperator: ["180-nvidia-gpu-operator.yaml"],
    OptionalServices.KEDA: ["180-keda.yaml"],
    OptionalServices.VPA: ["180-vpa.yaml"]
}


def build_argo_exclude_string(services: [str]) -> str:
    if not services:
        services = []
    oc_to_ignore = OPTIONAL_SERVICES_MAP.copy()
    for svc in services:
        oc_to_ignore.pop(svc)
    if oc_to_ignore:
        return str.join(", ", *oc_to_ignore.values())
    else:
        return ""
