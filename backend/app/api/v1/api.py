from fastapi import APIRouter

from app.api.v1.routes_analytics import router as analytics_router
from app.api.v1.routes_collaboration import router as collaboration_router
from app.api.v1.routes_incidents import router as incidents_router
from app.api.v1.routes_nl import router as nl_router

api_router = APIRouter()
api_router.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(nl_router, prefix="/nl", tags=["nl-query"])
api_router.include_router(collaboration_router, prefix="/collaboration", tags=["collaboration"])
