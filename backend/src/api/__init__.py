from backend.src.config import settings

import logging

from fastapi import APIRouter


logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"/{settings.API_VERSION}")


@router.get("/healthy", summary="Health Check", description="Check the health status of the API.")
async def healthy() -> bool:
    """Health check endpoint to verify that the API is running."""
    result = settings.CELERY.send_task("awwh")
    return result.get(timeout=10)


def init() -> APIRouter:
    from backend.src.api.routes import task
    router.include_router(task.router)
    logger.debug("api initialized")
    return router
