import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.tests import mockdata
from backend.src.database.user import (
    User,
    PasswordAuthentication
)


@pytest.mark.dependency(name='test_create_user')
async def test_create_user(session: AsyncSession) -> None:
    user = await User.create(
        session,
        email=mockdata.user.email,
        name=mockdata.user.name,
        description=mockdata.user.description
    )
    assert user.email == mockdata.user.email
    assert user.name == mockdata.user.name
    assert user.description == mockdata.user.description
    assert user.is_disabled is False
    assert user.is_deleted is False


@pytest.mark.dependency(depends=['test_create_user'])
async def test_query_user(session: AsyncSession) -> None:
    user_queried_by_email = await User.query(session, email=mockdata.user.email)
    assert user_queried_by_email is not None
    user_queried_by_id = await User.query(session, id=str(user_queried_by_email.id))
    assert user_queried_by_email == user_queried_by_id


@pytest.mark.dependency(depends=['test_create_user'])
async def test_create_password_authentication(session: AsyncSession) -> None:
    user = await User.query(session, email=mockdata.user.email)
    assert user is not None
    auth = await PasswordAuthentication.create(session, user=user, password=mockdata.password_auth.password)
    assert auth is not None
    assert auth.hashed_password != mockdata.password_auth.password
