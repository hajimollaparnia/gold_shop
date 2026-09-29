from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from apps.pricing.providers.external import (
    ExternalPriceProviderError,
    ServixPriceProvider,
)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "code": "GOLD_18_RLS",
            "value": "237072000",
            "businessTime": "2026-09-27T10:00:00Z",
        },
    ],
)
def test_servix_provider_parses_valid_response(payload):
    provider = ServixPriceProvider(api_key="test-api-key")

    response = Mock()
    response.status_code = 200
    response.json.return_value = payload

    with patch(
        "apps.pricing.providers.external.requests.get",
        return_value=response,
    ) as mock_get:
        prices = provider.fetch_prices()

    assert len(prices) == 1

    price = prices[0]

    assert price.asset == "gold"
    assert price.purity == 18
    assert price.buy_price == Decimal("237072000")
    assert price.sell_price == Decimal("237072000")
    assert price.currency == "IRR"
    assert price.source == "servix:GOLD_18_RLS"

    mock_get.assert_called_once()


def test_servix_provider_rejects_invalid_asset_code():
    provider = ServixPriceProvider(api_key="test-api-key")

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "code": "SILVER",
        "value": "100",
        "businessTime": "2026-09-27T10:00:00Z",
    }

    with patch(
        "apps.pricing.providers.external.requests.get",
        return_value=response,
    ):
        with pytest.raises(ExternalPriceProviderError):
            provider.fetch_prices()


def test_servix_provider_rejects_empty_price():
    provider = ServixPriceProvider(api_key="test-api-key")

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "code": "GOLD_18_RLS",
        "value": "",
        "businessTime": "2026-09-27T10:00:00Z",
    }

    with patch(
        "apps.pricing.providers.external.requests.get",
        return_value=response,
    ):
        with pytest.raises(ExternalPriceProviderError):
            provider.fetch_prices()


def test_servix_provider_rejects_http_error():
    provider = ServixPriceProvider(api_key="test-api-key")

    response = Mock()
    response.status_code = 401

    with patch(
        "apps.pricing.providers.external.requests.get",
        return_value=response,
    ):
        with pytest.raises(ExternalPriceProviderError):
            provider.fetch_prices()


def test_servix_provider_rejects_invalid_json():
    provider = ServixPriceProvider(api_key="test-api-key")

    response = Mock()
    response.status_code = 200
    response.json.side_effect = ValueError("Invalid JSON")

    with patch(
        "apps.pricing.providers.external.requests.get",
        return_value=response,
    ):
        with pytest.raises(ExternalPriceProviderError):
            provider.fetch_prices()