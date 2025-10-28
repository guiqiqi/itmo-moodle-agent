from backend.src.config import settings

import logging


logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

for handler in settings.LOG_HANDLERS:
    logger.addHandler(handler)


class BackendException(Exception):
    _base_code: int = 0
    _code: int
    msg: str

    @property
    def code(self) -> int:
        return self._code + self._base_code
