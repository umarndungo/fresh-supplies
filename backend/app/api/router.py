from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.ml import router as ml_router
from app.api.routes.mobile_auth import router as mobile_auth_router
from app.api.routes.mobile_devices import router as mobile_devices_router
from app.api.routes.mobile_driver import router as mobile_driver_router
from app.api.routes.mobile_shipments import router as mobile_shipments_router
from app.api.routes.produce import router as produce_router
from app.api.routes.shipments import router as shipments_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(shipments_router)
api_router.include_router(produce_router)
api_router.include_router(ml_router)
api_router.include_router(mobile_auth_router)
api_router.include_router(mobile_devices_router)
api_router.include_router(mobile_driver_router)
api_router.include_router(mobile_shipments_router)
