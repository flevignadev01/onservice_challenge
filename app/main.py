from fastapi import FastAPI

from app.api.journeys import router as journeys_router
from app.core.settings import settings

app = FastAPI(
    title=settings.app_name,
    docs_url=None if settings.environment == "production" else "/docs",
    openapi_url=None if settings.environment == "production" else "/openapi.json",
)

app.include_router(journeys_router, prefix="/journeys", tags=["journeys"])
