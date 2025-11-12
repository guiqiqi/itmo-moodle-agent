"""
Moodle Client for get student answer with format JSON.
The integration here for system.
"""
from __future__ import annotations

from pydantic import BaseModel

from backend.src import BackendException

import typing as t
import logging
from datetime import datetime
from abc import abstractmethod


logger = logging.getLogger(__name__)


class MoodleConfig(BaseModel):
    """Configuration for connecting to Moodle."""
    username: str
    password: str
    base_url: str
    service: t.Literal['moodle_mobile_app', '']


class Course(BaseModel):
    """Course strucutre."""
    id: int
    shortname: str
    fullname: str


class Assignment(BaseModel):
    """Assignment structure."""
    id: int
    name: str
    course: int
    intro: str
    duedate: t.Optional[datetime] = None
    allowsubmissionsfromdate: t.Optional[datetime] = None


class PluginProtocol(t.Protocol):
    type: t.ClassVar[str]

    @abstractmethod
    def handle(self) -> str: ...


class Plugin(BaseModel):
    """Plugin strucuture."""
    __metaclass__ = PluginProtocol

    type: str
    _registry: t.ClassVar[t.Dict[str, t.Type[Plugin]]] = {}

    def __init_subclass__(cls):
        if not hasattr(cls, 'type') or not isinstance(cls.type, str):
            raise TypeError(
                f"Class {cls.__name__} must define 'type' as a string ClassVar")
        cls._registry[cls.type] = cls

    @abstractmethod
    def handle(self) -> ...:
        raise NotImplementedError


class Submission(BaseModel):
    """Submission structure."""
    id: int
    assignment_id: int
    user_id: int
    status: str
    grade_status: str
    time_created: datetime
    time_modified: datetime
    plugins: t.List[Plugin]


class IntegrationException(BackendException):
    """Base exception for integration part."""
    _base_code: int = 10000
