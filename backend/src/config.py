from pydantic_settings import BaseSettings, SettingsConfigDict
import pydantic

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

    @pydantic.computed_field
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
        env_file=f'.env.{ENVIRONMENT}',
        env_file_encoding='utf-8'
    )


settings = Settings()
