from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.http import api_sports_headers, set_http_client
from app.services.billing_store import billing_store
from app.services.prediction_store import prediction_store
from app.services.sports.factory import init_sports_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_sports_registry()
    await billing_store.connect()
    await prediction_store.connect()
    async with httpx.AsyncClient(
        base_url=settings.sports_api_base_url.rstrip("/"),
        headers=api_sports_headers(settings.sports_api_key),
        timeout=30.0,
    ) as client:
        app.state.http_client = client
        set_http_client(client)
        yield
    set_http_client(None)
    await billing_store.close()
    await prediction_store.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Sports Predictor API",
        description="Multi-sport player prop analysis (MVP: soccer)",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "Sports Predictor API", "docs": "/docs"}

    return app


app = create_app()
