from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import get_billing_service
from app.core.clerk_auth import ClerkUser, get_current_clerk_user
from app.core.exceptions import AppError
from app.models.billing import (
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionStatusResponse,
    WebhookStatusResponse,
)
from app.services.billing_service import BillingService

router = APIRouter()


@router.get("/subscription-status", response_model=SubscriptionStatusResponse)
async def subscription_status(
    user: ClerkUser = Depends(get_current_clerk_user),
    billing: BillingService = Depends(get_billing_service),
):
    """Return whether the authenticated user has an active subscription."""
    try:
        status = await billing.verify_active_subscription(user)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return SubscriptionStatusResponse(
        active=status.active,
        status=status.status,
        is_admin=status.is_admin,
    )


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    user: ClerkUser = Depends(get_current_clerk_user),
    billing: BillingService = Depends(get_billing_service),
):
    """Create a Stripe Checkout session for the authenticated Clerk user."""
    try:
        result = billing.create_checkout_session(user.user_id)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return CheckoutSessionResponse(**result)


@router.post("/customer-portal", response_model=PortalSessionResponse)
async def create_customer_portal_session(
    user: ClerkUser = Depends(get_current_clerk_user),
    billing: BillingService = Depends(get_billing_service),
):
    """Create a Stripe Customer Portal session for the authenticated user."""
    try:
        result = await billing.create_customer_portal_session(user.user_id)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return PortalSessionResponse(**result)


@router.post("/webhook", response_model=WebhookStatusResponse)
async def stripe_webhook(
    request: Request,
    billing: BillingService = Depends(get_billing_service),
):
    """Stripe webhook listener — verifies signature and updates billing cache."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = billing.construct_webhook_event(payload, signature)
        await billing.handle_webhook_event(event)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return WebhookStatusResponse(status="success")

