from __future__ import annotations

from fastapi import FastAPI

from app.api.auto_calibration_routes import router as auto_calibration_router
from app.api.integration_routes import router as integration_router
from app.api.routes import router

app = FastAPI(title="Okada Governance Kernel", version="1.11.0")
app.include_router(router)
app.include_router(auto_calibration_router)
app.include_router(integration_router)
