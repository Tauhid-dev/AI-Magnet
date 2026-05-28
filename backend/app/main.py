"""FastAPI application entrypoint."""

import logging
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import bind_request_id, configure_logging, reset_request_id
from app.core.security import apply_security_headers

request_logger = logging.getLogger("app.request")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    settings.validate_runtime_security()
    configure_logging(settings.log_level, settings.log_format)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url="/redoc" if settings.enable_api_docs else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-AI-Magnet-CSRF"],
    )

    @app.middleware("http")
    async def request_context_middleware(request, call_next):
        request_id = request.headers.get(settings.request_id_header) or str(uuid4())
        token = bind_request_id(request_id)
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            status_code = getattr(response, "status_code", 500)
            if response is not None:
                response.headers[settings.request_id_header] = request_id
                response.headers["X-Correlation-ID"] = request_id
                apply_security_headers(response.headers)
            request_logger.info(
                "request_completed method=%s path=%s status_code=%s",
                request.method,
                request.url.path,
                status_code,
            )
            reset_request_id(token)

    app.include_router(api_router)
    return app


app = create_app()
