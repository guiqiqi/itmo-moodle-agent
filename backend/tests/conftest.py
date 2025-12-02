import pytest_asyncio as pytest
from sqlmodel.ext.asyncio.session import AsyncSession

import typing as t

from backend.src.config import settings
from backend.src.integration.client import (
    APIClient,
    MoodleConfig
)
from backend.src.database import init, engine


@pytest.fixture(scope='session')
async def nothing() -> None:
    """Nothing will be provided by this fixture. Liternally nothing."""
    return None


@pytest.fixture(scope='session')
async def config() -> MoodleConfig:
    """Moodle configuration for tests."""
    return MoodleConfig(
        username=settings.MOODLE_USERNAME,
        password=settings.MOODLE_PASSWORD,
        base_url=settings.MOODLE_BASE_URL,
        service=settings.MOODLE_SERVICE,
    )


@pytest.fixture(scope='session')
async def client(config: MoodleConfig) -> t.AsyncGenerator[APIClient, None]:
    """Moodle API client for tests."""
    async with APIClient(config) as client:
        yield client


@pytest.fixture(scope='session', autouse=True)
async def session() -> t.AsyncGenerator[AsyncSession, None]:
    """Fixture to initialize and provide a database session for tests."""
    async with AsyncSession(engine) as session:
        await init()
        yield session
