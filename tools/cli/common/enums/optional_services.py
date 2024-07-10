"""Optional CG DevX platform services enums."""
import enum

from common.const.const import DEFAULT_ENUM_VALUE


class OptionalServices(str, enum.Enum):
    """List of all CG DevX platform optional services."""

    NvidiaGpuOperator = "nvidia-gpu-operator"
    VPA = "vpa"
    KEDA = "keda"
    KUBEVIRT = "kubevirt"

    @classmethod
    def has_value(cls, value) -> bool:
        """
        Check if value defined.

        :param value: Value
        :return: True or False
        """
        return value in cls._value2member_map_

    @classmethod
    def can_ignore(cls, value):
        """
        Check if the state passed from the request is 'unknown' and event can be ignored.

        :param value: str
        :return: return True if the state is unknown, otherwise return False.
        """
        if value == DEFAULT_ENUM_VALUE:
            return True
        return False
