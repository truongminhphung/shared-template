"""Unit tests for UserService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFound,
    DuplicateResource,
    ValidationError,
)
from app.db.tables.users import User
from app.services.user_service import UserService


@pytest.mark.unit
class TestUserServiceListUsers:
    """Test UserService.list_users method."""

    async def test_list_users_empty_database(self):
        """Test listing users when database is empty."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        # Act
        users = await service.list_users()

        # Assert
        assert users == []
        mock_session.execute.assert_called_once()

    async def test_list_users_with_multiple_users(self):
        """Test listing users when multiple users exist."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        mock_users = [
            User(id=1, email="user1@example.com", user_name="user1", is_active=True),
            User(id=2, email="user2@example.com", user_name="user2", is_active=True),
            User(id=3, email="user3@example.com", user_name="user3", is_active=False),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        # Act
        users = await service.list_users()

        # Assert
        assert len(users) == 3
        assert users[0].email == "user1@example.com"
        assert users[1].user_name == "user2"
        assert users[2].is_active is False


@pytest.mark.unit
class TestUserServiceGetUser:
    """Test UserService.get_user method."""

    async def test_get_user_success(self):
        """Test successfully retrieving a user by ID."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_user = User(
            id=1, email="test@example.com", user_name="testuser", is_active=True
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        # Act
        user = await service.get_user(1)

        # Assert
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.user_name == "testuser"
        mock_session.execute.assert_called_once()

    async def test_get_user_not_found(self):
        """Test getting a non-existent user raises ResourceNotFound."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ResourceNotFound) as exc_info:
            await service.get_user(999)

        assert exc_info.value.entity_name == "User"
        assert exc_info.value.entity_id == 999


@pytest.mark.unit
class TestUserServiceCreateUser:
    """Test UserService.create_user method."""

    async def test_create_user_success(self):
        """Test successfully creating a user."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock the email uniqueness check (no existing user)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock add, commit, and refresh
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        # Mock refresh to set the is_active field since the User __init__ sets it
        async def mock_refresh(obj):
            if not hasattr(obj, "is_active") or obj.is_active is None:
                obj.is_active = True

        mock_session.refresh = AsyncMock(side_effect=mock_refresh)

        service = UserService(mock_session)

        # Act
        user = await service.create_user(email="new@example.com", user_name="newuser")

        # Assert
        assert user.email == "new@example.com"
        assert user.user_name == "newuser"
        assert user.is_active is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_create_user_empty_email(self):
        """Test creating a user with empty email raises ValidationError."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_user(email="", user_name="testuser")

        assert "Email cannot be empty" in exc_info.value.message

    async def test_create_user_whitespace_email(self):
        """Test creating a user with whitespace-only email raises ValidationError."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_user(email="   ", user_name="testuser")

        assert "Email cannot be empty" in exc_info.value.message

    async def test_create_user_empty_username(self):
        """Test creating a user with empty username raises ValidationError."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_user(email="test@example.com", user_name="")

        assert "Username cannot be empty" in exc_info.value.message

    async def test_create_user_whitespace_username(self):
        """Test creating a user with whitespace-only username raises ValidationError."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_user(email="test@example.com", user_name="   ")

        assert "Username cannot be empty" in exc_info.value.message

    async def test_create_user_duplicate_email(self):
        """Test creating a user with duplicate email raises DuplicateResource."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock existing user with same email
        existing_user = User(
            id=1, email="existing@example.com", user_name="existinguser", is_active=True
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = existing_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(DuplicateResource) as exc_info:
            await service.create_user(email="existing@example.com", user_name="newuser")

        assert exc_info.value.entity_name == "User"
        assert exc_info.value.field_name == "email"
        assert exc_info.value.field_value == "existing@example.com"

    async def test_create_user_both_empty_fields(self):
        """Test creating a user with both empty email and username."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        service = UserService(mock_session)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_user(email="", user_name="")

        # Should raise for email first (checked first in the code)
        assert "Email cannot be empty" in exc_info.value.message
