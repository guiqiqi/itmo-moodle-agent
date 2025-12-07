from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from pydantic import (
    RedisDsn,
    PostgresDsn,
    computed_field
)
import celery

import typing as t
import logging
import logging.handlers as lhandlers


class Settings(BaseSettings):

    # Base project settings
    PROJECT_NAME: str = 'itmo-moodle-agent'
    ENVIRONMENT: t.Literal[
        'test', 'dev', 'prod'
    ] = 'test'

    # Logger settings
    LOG_LEVEL: t.Literal[
        'DEBUG', 'INFO', 'WARNING',
        'ERROR', 'CRITICAL'
    ] = 'DEBUG'
    LOG_FORMAT: str = '[%(asctime)s] [%(levelname)s] %(message)s'
    LOG_FILE: str = f'logs/{PROJECT_NAME}.log'
    LOG_FILE_MAXSIZE: int = 1024 * 1024
    LOG_FILE_AUTOBACKUP: int = 10

    @computed_field
    @property
    def LOG_HANDLERS(self) -> t.List[logging.Handler]:
        handlers = []
        handlers.append(logging.StreamHandler())
        if self.LOG_FILE:
            handler = lhandlers.RotatingFileHandler(
                self.LOG_FILE,
                maxBytes=self.LOG_FILE_MAXSIZE,
                backupCount=self.LOG_FILE_AUTOBACKUP,
            )
            handlers.append(handler)
        return handlers

    # Moodle integration settings
    MOODLE_BASE_URL: str = 'https://moodle.example.com/m'

    # Development and testing configurations
    MOODLE_USERNAME: str = 'user'
    MOODLE_PASSWORD: str = 'pass'
    MOODLE_SERVICE: t.Literal['moodle_mobile_app', ''] = 'moodle_mobile_app'

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=f'.env',
        env_file_encoding='utf-8'
    )

    # Database settings
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = ''

    @computed_field
    @property
    def DATABASE_URI(self) -> PostgresDsn | str:
        """Use SQLite memory database when in testing enviroment."""
        if self.ENVIRONMENT == 'test':
            return 'sqlite+aiosqlite:///:memory:'

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )

    # Celery Broker settings
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_BROKER_DB: int = 0
    REDIS_PASSWORD: str = ''

    @computed_field
    @property
    def REDIS_URI(self) -> RedisDsn:
        """Building Redis URI for Celery and caching."""
        return RedisDsn.build(
            scheme='redis',
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_BROKER_DB),
            password=self.REDIS_PASSWORD or None
        )

    # Celery dispatcher settings
    CELERY_TASK_QUEUE: str = 'tasks'

    @computed_field
    @property
    def CELERY(self) -> celery.Celery:
        """Build celery instance using settings."""
        return celery.Celery(
            self.CELERY_TASK_QUEUE,
            broker=str(self.REDIS_URI),
            backend=str(self.REDIS_URI)
        )


settings = Settings()
