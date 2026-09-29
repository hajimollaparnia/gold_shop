from datetime import datetime
from decimal import Decimal, InvalidOperation

import requests

from .base import MarketPriceData, PriceProvider


class ExternalPriceProviderError(Exception):
    """Raised when the external market price provider fails."""


class ServixPriceProvider(PriceProvider):
    """
    Fetches the current 18K gold price from Servix.

    Servix asset:
        GOLD_18_RLS

    The API key is intentionally read from Django settings
    and is never exposed to the frontend.
    """

    ASSET_CODE = "GOLD_18_RLS"
    ENDPOINT = (
        "https://servix.cc/api/v1/assets/"
        f"{ASSET_CODE}"
    )

    def __init__(
        self,
        *,
        api_key: str,
        timeout: tuple[float, float] = (3.0, 10.0),
    ) -> None:
        if not api_key:
            raise ValueError("Servix API key is required.")

        self.api_key = api_key
        self.timeout = timeout

    def fetch_prices(self) -> list[MarketPriceData]:
        """Fetch and normalize the current 18K gold price."""

        try:
            response = requests.get(
                self.ENDPOINT,
                headers={
                    "X-API-Key": self.api_key,
                    "Accept": "application/json",
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ExternalPriceProviderError(
                "Unable to connect to Servix."
            ) from exc

        if response.status_code != 200:
            raise ExternalPriceProviderError(
                f"Servix returned HTTP {response.status_code}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ExternalPriceProviderError(
                "Servix returned invalid JSON."
            ) from exc

        return [self._parse_payload(payload)]

    def _parse_payload(
        self,
        payload: dict,
    ) -> MarketPriceData:
        """Validate and normalize the Servix response."""

        if payload.get("code") != self.ASSET_CODE:
            raise ExternalPriceProviderError(
                "Unexpected asset code returned by Servix."
            )

        raw_value = payload.get("value")

        if raw_value in (None, ""):
            raise ExternalPriceProviderError(
                "Servix returned an empty price."
            )

        try:
            price = Decimal(str(raw_value))
        except (InvalidOperation, ValueError) as exc:
            raise ExternalPriceProviderError(
                "Servix returned an invalid price."
            ) from exc

        if price < Decimal("0"):
            raise ExternalPriceProviderError(
                "Servix returned a negative price."
            )

        raw_timestamp = payload.get("businessTime")

        if raw_timestamp:
            try:
                timestamp = datetime.fromisoformat(
                    raw_timestamp.replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise ExternalPriceProviderError(
                    "Servix returned an invalid businessTime."
                ) from exc
        else:
            timestamp = datetime.now().astimezone()

        return MarketPriceData(
            asset="gold",
            purity=18,
            buy_price=price,
            sell_price=price,
            currency="IRR",
            source="servix:GOLD_18_RLS",
            timestamp=timestamp,
        )