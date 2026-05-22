"""Top-level API router."""

from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.business_portal import router as business_portal_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.widget import router as widget_router


api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(business_portal_router)
api_router.include_router(chat_router)
api_router.include_router(health_router)
api_router.include_router(widget_router)
