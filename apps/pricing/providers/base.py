from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MarketPriceData:
    """
    Normalized and validated market price data.

    This object represents market data only.
    It does not contain database or product pricing logic.
    """

    asset: str
    buy_price: Decimal
    sell_price: Decimal
    currency: str
    source: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """Validate market price data invariants."""

        if not self.asset.strip():
            raise ValueError("asset must not be empty.")

        if not self.currency.strip():
            raise ValueError("currency must not be empty.")

        if not self.source.strip():
            raise ValueError("source must not be empty.")

        if self.buy_price < Decimal("0"):
            raise ValueError("buy_price must not be negative.")

        if self.sell_price < Decimal("0"):
            raise ValueError("sell_price must not be negative.")

        if self.sell_price < self.buy_price:
            raise ValueError(
                "sell_price must be greater than or equal to buy_price."
            )


class PriceProvider(ABC):
    """
    Contract for market price providers.

    Concrete providers must implement this interface.
    Pricing business logic must depend on this abstraction,
    not on a specific external API.
    """

    @abstractmethod
    def fetch_prices(self) -> list[MarketPriceData]:
        """
        Fetch and normalize current market prices.

        Returns:
            A list of normalized market price records.
        """
        raise NotImplementedError