from src.config import settings

import logging

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

logger = logging.getLogger(__name__)
engine = create_async_engine(str(settings.DATABASE_URI))


async def init() -> AsyncEngine:
    """Initialize database connection."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.debug("database initialized")
    return engine
