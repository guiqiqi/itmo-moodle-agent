from backend.src.database.user import User

from httpx import AsyncClient


async def test_nonexistent_access_token(api: AsyncClient) -> None:
    """Test access to protected route without token."""
    response = await api.get(f"/auth/me")
    assert response.status_code == 401


async def test_invalid_login(api: AsyncClient, user: User) -> None:
    """Test login with invalid credentials."""
    response = await api.post(
        "/auth/basic/login",
        data={
            "username": user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


async def test_get_current_user(
    api: AsyncClient,
    token: str
) -> None:
    """Test retrieval of current user information."""
    response = await api.get(
        f"/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    data = response.json()
    assert "email" in data
    assert "name" in data
    assert "description" in data
    assert "groups" in data


async def test_group_privelege(
    api: AsyncClient,
    token: str
) -> None:
    """Test access to a route requiring specific group membership."""
    response = await api.get(
        f"/auth/confidential",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


async def test_user_password_registration(
    api: AsyncClient
) -> None:
    """Test user registration."""
    response = await api.post(
        "/auth/basic/register",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "name" in data
    assert "description" in data
    assert "groups" in data

    # Login test for just created user
    response = await api.post(
        "/auth/basic/login",
        data={
            "username": "test@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
