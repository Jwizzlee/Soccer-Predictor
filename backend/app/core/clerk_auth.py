"""Clerk JWT verification for protected backend routes."""

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class ClerkUser:
    user_id: str
    email: str | None = None


@lru_cache
def _jwks_client(issuer: str) -> PyJWKClient:
    issuer = issuer.rstrip("/")
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", cache_keys=True)


def _verify_clerk_token(token: str) -> ClerkUser:
    settings = get_settings()
    if not settings.clerk_jwt_issuer:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_JWT_ISSUER is not configured on the server",
        )

    try:
        signing_key = _jwks_client(settings.clerk_jwt_issuer).get_signing_key_from_jwt(
            token
        )
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_jwt_issuer.rstrip("/"),
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Clerk session token: {exc}",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clerk token missing user id",
        )

    email = _extract_email_from_payload(payload)
    return ClerkUser(user_id=user_id, email=email)


def _extract_email_from_payload(payload: dict) -> str | None:
    direct = payload.get("email")
    if isinstance(direct, str) and direct.strip():
        return direct.strip().lower()

    primary = payload.get("primary_email_address")
    if isinstance(primary, str) and primary.strip():
        return primary.strip().lower()

    return None


async def get_current_clerk_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> ClerkUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _verify_clerk_token(credentials.credentials)
