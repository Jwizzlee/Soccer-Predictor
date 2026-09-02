from collections.abc import AsyncGenerator

import httpx
from fastapi import Depends, Request

from app.core.clerk_auth import ClerkUser, get_current_clerk_user
from app.core.exceptions import SubscriptionRequiredError
from app.services.billing_service import BillingService
from app.services.prediction_service import PredictionService


async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_prediction_service() -> PredictionService:
    return PredictionService()


def get_billing_service() -> BillingService:
    return BillingService()


async def require_active_subscription(
    user: ClerkUser = Depends(get_current_clerk_user),
    billing: BillingService = Depends(get_billing_service),
) -> ClerkUser:
    status = await billing.verify_active_subscription(user)
    if not status.active:
        raise SubscriptionRequiredError()
    return user


async def lifespan_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client
