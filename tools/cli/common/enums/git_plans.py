"""Git provider subscription types enums."""
import enum

from common.const.const import DEFAULT_ENUM_VALUE


class GitSubscriptionPlans(int, enum.Enum):
    """List of standardized Git provider subscription plans."""

    Free = 0
    Pro = 1
    Enterprise = 2
