from backend.src.config import settings

import typing_extensions as te
from datetime import datetime, timezone, timedelta

import jwt
from sqlmodel import SQLModel
from pydantic import model_validator


class JWTTokenPayload(SQLModel):
    sub: str
    iat: datetime
    exp: datetime

    @model_validator(mode="after")
    def validate_token_timestamp(self) -> te.Self:
        now = datetime.now(timezone.utc)
        if self.exp < now:
            raise ValueError("token is expired")
        if self.iat > now:
            raise ValueError("token was issued in the future")
        return self


class JWTToken(SQLModel):
    access_token: str
    token_type: str = "bearer"

    @classmethod
    def create_access_token(cls, *, subject: str) -> te.Self:
        """Create a new JWT access token."""
        now = datetime.now(timezone.utc)
        payload = JWTTokenPayload(
            sub=subject, iat=now,
            exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return cls(
            access_token=jwt.encode(
                payload.model_dump(),
                key=settings.SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
        )
