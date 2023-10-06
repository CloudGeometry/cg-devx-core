"""DNS registrars enums."""
import enum

from common.const.const import DEFAULT_ENUM_VALUE


class DnsRegistrars(str, enum.Enum):
    """List of possible DNS Registrars."""

    Route53 = 'route53'
    AzureDNS = 'azure_dns'

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
