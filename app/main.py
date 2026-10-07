from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import logger

from app.db.session import engine
from app.db.base import Base
# Make sure models are imported so they are registered with Base
from app.models.file_record import FileRecord
from app.models.feature_record import FeatureRecord

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up API...")
        Base.metadata.create_all(bind=engine)

    return app

app = create_app()

@app.get("/health")
def root_health():
    """Root health check."""
    return {"status": "ok"}
