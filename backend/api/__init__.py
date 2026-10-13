from fastapi import APIRouter
from backend.api import health, tickets, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tickets.router, prefix="/api", tags=["tickets"])
api_router.include_router(ui.router, tags=["ui"])
