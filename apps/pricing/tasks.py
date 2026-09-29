import logging

from celery import shared_task
from django.conf import settings

from apps.pricing.providers.external import (
    ExternalPriceProviderError,
    ServixPriceProvider,
)
from apps.pricing.services.market_price_sync import MarketPriceSyncService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(ExternalPriceProviderError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def sync_market_prices(self):
    """
    Synchronize market prices from the configured external provider.

    The task delegates business logic to MarketPriceSyncService.
    """

    if not settings.SERVIX_API_KEY:
        logger.error("SERVIX_API_KEY is not configured.")
        return {
            "status": "failed",
            "reason": "SERVIX_API_KEY is not configured.",
        }

    provider = ServixPriceProvider(
        api_key=settings.SERVIX_API_KEY,
    )

    service = MarketPriceSyncService(provider)

    created_prices = service.sync()

    logger.info(
        "Market price sync completed successfully. Created %s price(s).",
        len(created_prices),
    )

    return {
        "status": "success",
        "created": len(created_prices),
    }