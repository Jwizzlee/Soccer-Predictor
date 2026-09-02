from dataclasses import dataclass

import httpx
import stripe

from app.core.config import get_settings
from app.core.clerk_auth import ClerkUser
from app.core.exceptions import AppError
from app.services.billing_store import billing_store


@dataclass(frozen=True)
class SubscriptionStatus:
    active: bool
    status: str
    is_admin: bool = False


class BillingService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.stripe_secret_key:
            raise AppError("STRIPE_SECRET_KEY is not configured", status_code=500)
        if not settings.stripe_price_id:
            raise AppError("STRIPE_PRICE_ID is not configured", status_code=500)
        stripe.api_key = settings.stripe_secret_key
        self._price_id = settings.stripe_price_id
        self._frontend_url = settings.frontend_url.rstrip("/")
        self._settings = settings

    def create_checkout_session(self, clerk_user_id: str) -> dict[str, str]:
        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": self._price_id, "quantity": 1}],
                client_reference_id=clerk_user_id,
                metadata={"clerk_user_id": clerk_user_id},
                subscription_data={
                    "metadata": {"clerk_user_id": clerk_user_id},
                },
                success_url=(
                    f"{self._frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}"
                ),
                cancel_url=f"{self._frontend_url}/",
            )
        except stripe.StripeError as exc:
            raise AppError(
                f"Stripe error: {exc.user_message or str(exc)}", status_code=502
            ) from exc

        if not session.url:
            raise AppError("Stripe did not return a checkout URL", status_code=502)

        return {"url": session.url, "session_id": session.id}

    async def create_customer_portal_session(self, clerk_user_id: str) -> dict[str, str]:
        customer_id = await self._find_stripe_customer_id(clerk_user_id)
        if not customer_id:
            raise AppError(
                "No Stripe billing account found for this user. "
                "Subscribe first to manage billing.",
                status_code=404,
            )

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{self._frontend_url}/profile",
            )
        except stripe.StripeError as exc:
            raise AppError(
                f"Stripe error: {exc.user_message or str(exc)}", status_code=502
            ) from exc

        if not session.url:
            raise AppError("Stripe did not return a portal URL", status_code=502)

        return {"url": session.url}

    def construct_webhook_event(self, payload: bytes, signature_header: str):
        if not self._settings.stripe_webhook_secret:
            raise AppError("STRIPE_WEBHOOK_SECRET is not configured", status_code=500)

        try:
            return stripe.Webhook.construct_event(
                payload,
                signature_header,
                self._settings.stripe_webhook_secret,
            )
        except ValueError as exc:
            raise AppError(f"Invalid webhook payload: {exc}", status_code=400) from exc
        except stripe.SignatureVerificationError as exc:
            raise AppError(f"Invalid webhook signature: {exc}", status_code=400) from exc

    async def handle_webhook_event(self, event: stripe.Event) -> None:
        event_type = event["type"]
        data_object = event["data"]["object"]

        if event_type == "checkout.session.completed":
            await self._handle_checkout_session_completed(data_object)
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(data_object)
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(data_object)

    async def _handle_checkout_session_completed(self, session: dict) -> None:
        metadata = session.get("metadata") or {}
        clerk_user_id = metadata.get("clerk_user_id") or session.get("client_reference_id")
        customer_id = session.get("customer")

        if clerk_user_id and customer_id:
            await billing_store.set_customer_mapping(clerk_user_id, str(customer_id))

        if clerk_user_id and session.get("subscription"):
            await billing_store.set_subscription(clerk_user_id, True, "active")

    async def _handle_subscription_updated(self, subscription: dict) -> None:
        clerk_user_id = await self._clerk_user_id_from_subscription(subscription)
        if not clerk_user_id:
            return

        stripe_status = subscription.get("status", "unknown")
        active = stripe_status in ("active", "trialing")
        await billing_store.set_subscription(clerk_user_id, active, stripe_status)

        customer_id = subscription.get("customer")
        if customer_id:
            await billing_store.set_customer_mapping(clerk_user_id, str(customer_id))

    async def _handle_subscription_deleted(self, subscription: dict) -> None:
        clerk_user_id = await self._clerk_user_id_from_subscription(subscription)
        if not clerk_user_id:
            return

        await billing_store.set_subscription(clerk_user_id, False, "canceled")

    async def _clerk_user_id_from_subscription(self, subscription: dict) -> str | None:
        metadata = subscription.get("metadata") or {}
        clerk_user_id = metadata.get("clerk_user_id")
        if clerk_user_id:
            return str(clerk_user_id)

        customer_id = subscription.get("customer")
        if customer_id:
            return await billing_store.get_clerk_user_id(str(customer_id))

        return None

    async def verify_active_subscription(self, user: ClerkUser) -> SubscriptionStatus:
        email = self._resolve_user_email(user)
        if self._is_admin_email(email):
            return SubscriptionStatus(active=True, status="admin", is_admin=True)

        cached = await billing_store.get_subscription(user.user_id)
        if cached is not None:
            if cached.active:
                return SubscriptionStatus(active=True, status=cached.status)
            return SubscriptionStatus(active=False, status=cached.status)

        if await self._has_active_stripe_subscription(user.user_id):
            await billing_store.set_subscription(user.user_id, True, "active")
            return SubscriptionStatus(active=True, status="active")

        return SubscriptionStatus(active=False, status="inactive")

    def _resolve_user_email(self, user: ClerkUser) -> str | None:
        if user.email:
            return user.email.strip().lower()

        if not self._settings.clerk_secret_key:
            return None

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"https://api.clerk.com/v1/users/{user.user_id}",
                    headers={"Authorization": f"Bearer {self._settings.clerk_secret_key}"},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return None

        addresses = data.get("email_addresses") or []
        primary_id = data.get("primary_email_address_id")
        for entry in addresses:
            if entry.get("id") == primary_id:
                return (entry.get("email_address") or "").strip().lower() or None

        if addresses:
            return (addresses[0].get("email_address") or "").strip().lower() or None

        return None

    def _is_admin_email(self, email: str | None) -> bool:
        if not email:
            return False

        normalized = email.strip().lower()
        local_part = normalized.split("@", 1)[0]

        for rule in self._settings.admin_email_rules:
            if "@" in rule:
                if normalized == rule:
                    return True
            elif local_part.startswith(rule) or normalized.startswith(rule):
                return True

        return False

    async def _has_active_stripe_subscription(self, clerk_user_id: str) -> bool:
        try:
            for status in ("active", "trialing"):
                result = stripe.Subscription.search(
                    query=(
                        f"metadata['clerk_user_id']:'{clerk_user_id}' "
                        f"AND status:'{status}'"
                    ),
                    limit=1,
                )
                if result.data:
                    return True

            sessions = stripe.checkout.Session.list(limit=20)
            for session in sessions.data:
                if session.client_reference_id != clerk_user_id:
                    continue
                if session.status != "complete" or not session.subscription:
                    continue
                subscription = stripe.Subscription.retrieve(session.subscription)
                if subscription.status in ("active", "trialing"):
                    return True
        except stripe.StripeError as exc:
            raise AppError(
                f"Stripe subscription lookup failed: {exc.user_message or str(exc)}",
                status_code=502,
            ) from exc

        return False

    async def _find_stripe_customer_id(self, clerk_user_id: str) -> str | None:
        cached_customer_id = await billing_store.get_customer_id(clerk_user_id)
        if cached_customer_id:
            return cached_customer_id

        try:
            subscriptions = stripe.Subscription.search(
                query=f"metadata['clerk_user_id']:'{clerk_user_id}'",
                limit=1,
            )
            if subscriptions.data:
                customer_id = self._stripe_customer_id(subscriptions.data[0].customer)
                await billing_store.set_customer_mapping(clerk_user_id, customer_id)
                return customer_id

            sessions = stripe.checkout.Session.list(limit=100)
            for session in sessions.data:
                if session.client_reference_id != clerk_user_id:
                    continue
                if session.customer:
                    customer_id = self._stripe_customer_id(session.customer)
                    await billing_store.set_customer_mapping(clerk_user_id, customer_id)
                    return customer_id
        except stripe.StripeError as exc:
            raise AppError(
                f"Stripe customer lookup failed: {exc.user_message or str(exc)}",
                status_code=502,
            ) from exc

        return None

    @staticmethod
    def _stripe_customer_id(customer: str | stripe.Customer) -> str:
        if isinstance(customer, str):
            return customer
        return customer.id
