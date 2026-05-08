from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import admin, ai, auth, catalogue, orders, users, vendor, vendors, wallet, webhooks
from app.utils.limiter import limiter


logger = logging.getLogger("venzap")


def error_payload(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


app = FastAPI(
    title="Venzap API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_urls,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logger.info("CORS allow_origins=%s", settings.frontend_urls)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("http_error", str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Convert Pydantic errors to JSON-serializable format
    errors = [
        {
            "loc": list(err.get("loc", [])),
            "msg": err.get("msg", "Unknown error"),
            "type": err.get("type", "unknown"),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_payload("validation_error", "Invalid request.", errors),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload("internal_server_error", "An unexpected error occurred."),
    )


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "name": settings.app_name, "environment": settings.environment}


app.include_router(auth.router)
app.include_router(vendor.router)
app.include_router(vendors.router)
app.include_router(catalogue.router)
app.include_router(users.router)
app.include_router(wallet.router)
app.include_router(orders.router)
app.include_router(webhooks.router)
app.include_router(ai.router)
app.include_router(admin.router)
