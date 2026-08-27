from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.scenes import router as scenes_router
from app.api.v1.detections import router as detections_router
from app.api.v1.drift import router as drift_router
from app.api.v1.ais import router as ais_router
from app.api.v1.vessels import router as vessels_router
from app.api.v1.attribution import router as attribution_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(incidents_router)
api_router.include_router(scenes_router)
api_router.include_router(detections_router)
api_router.include_router(drift_router)
api_router.include_router(ais_router)
api_router.include_router(vessels_router)
api_router.include_router(attribution_router)
api_router.include_router(investigations_router)
api_router.include_router(admin_router)
