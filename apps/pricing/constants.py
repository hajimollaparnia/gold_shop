from enum import StrEnum


class PricingType(StrEnum):
    """Supported pricing calculation types."""

    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"


# Backward-compatible alias
MakingFeeType = PricingType