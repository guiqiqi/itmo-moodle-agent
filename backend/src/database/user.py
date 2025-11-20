import typing as t
import typing_extensions as te
import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext


PasswordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserGroup(SQLModel, table=True):
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="user.id", primary_key=True
    )
    group_id: uuid.UUID = Field(
        nullable=False, foreign_key="group.id", primary_key=True, ondelete="CASCADE"
    )

    time_created: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc).replace(tzinfo=None),
        nullable=False
    )


class Group(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=1024)

    time_created: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc).replace(tzinfo=None),
        nullable=False
    )

    users: t.List["User"] = Relationship(
        back_populates="groups", link_model=UserGroup
    )

    @classmethod
    async def create(cls, session: AsyncSession, *, name: str, **extra_fields: t.Any) -> te.Self:
        """Create a new group."""
        group = cls(name=name, **extra_fields)
        session.add(group)
        await session.commit()
        await session.refresh(group)
        return group

    async def delete(self, session: AsyncSession) -> None:
        """Delete the group."""
        await session.delete(self)
        await session.commit()

    @classmethod
    async def list(cls, session: AsyncSession) -> t.List[te.Self]:
        """List all groups."""
        groups = await session.exec(select(cls))
        return list(groups.unique().all())

    @classmethod
    async def query(cls, session: AsyncSession, *, id: str | None = None, name: str | None = None) -> te.Self | None:
        """Query group by id or name."""
        if id:
            return await session.get(cls, id)
        if name:
            group = await session.exec(
                select(cls).where(cls.name == name)
            )
            return group.first() if group else None
        return None

    async def add_user(self, session: AsyncSession, *, user: "User") -> None:
        """Add a user to the group."""
        await session.refresh(self, attribute_names=["users"])
        if user not in self.users:
            self.users.append(user)
            session.add(self)
            await session.commit()
            await session.refresh(self, attribute_names=["users"])

    async def remove_user(self, session: AsyncSession, *, user: "User") -> None:
        """Remove a user from the group."""
        await session.refresh(self, attribute_names=["users"])
        if user in self.users:
            self.users.remove(user)
            session.add(self)
            await session.commit()
            await session.refresh(self)
            await session.refresh(self, attribute_names=["users"])


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)

    is_disabled: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    time_created: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    time_updated: datetime | None = Field(default=None)
    time_deleted: datetime | None = Field(default=None)

    groups: t.List[Group] = Relationship(
        back_populates="users", link_model=UserGroup
    )

    @classmethod
    async def create(cls, session: AsyncSession, *, email: str, **extra_fields: t.Any) -> te.Self:
        """Create a new user."""
        user = cls(
            email=email,
            **extra_fields
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession) -> None:
        """Soft delete the user by setting is_deleted to True and updating time_deleted."""
        self.is_deleted = True
        self.time_deleted = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(self)
        await session.commit()
        await session.refresh(self)

    @classmethod
    async def query(cls, session: AsyncSession, *, id: str | None = None, email: str | None = None) -> te.Self | None:
        """Query user by id or email."""
        if id:
            return await session.get(cls, uuid.UUID(id))
        if email:
            user = await session.exec(
                select(cls).where(cls.email == email)
            )
            return user.first() if user else None
        return None
