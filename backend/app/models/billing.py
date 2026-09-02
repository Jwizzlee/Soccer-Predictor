from pydantic import BaseModel, HttpUrl


class CheckoutSessionResponse(BaseModel):
    url: HttpUrl
    session_id: str


class SubscriptionStatusResponse(BaseModel):
    active: bool
    status: str
    is_admin: bool = False


class PortalSessionResponse(BaseModel):
    url: HttpUrl


class WebhookStatusResponse(BaseModel):
    status: str
