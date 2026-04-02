from __future__ import annotations

from fastapi import FastAPI

from api.routes.admin import router as admin_router
from api.routes.batch import router as batch_router
from api.routes.catalog import router as catalog_router
from api.routes.executions import router as executions_router
from api.routes.health import router as health_router
from api.routes.plugins import router as plugins_router
from api.routes.workflows import router as workflows_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Workflow Automation Engine")
    app.include_router(health_router, tags=["health"])
    app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
    app.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
    app.include_router(executions_router, prefix="/executions", tags=["executions"])
    app.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    app.include_router(batch_router, prefix="/batch", tags=["batch"])
    return app


app = create_app()
