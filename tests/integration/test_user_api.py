"""Integration tests for User API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestListUsersEndpoint:
    """Test GET /api/v1/users endpoint."""

    async def test_list_users_empty_database(self, async_client: AsyncClient):
        """Test listing users when database is empty."""
        # Act
        response = await async_client.get("/api/v1/users")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_users_with_data(self, async_client: AsyncClient, created_users):
        """Test listing users when users exist."""
        # Act
        response = await async_client.get("/api/v1/users")

        # Assert
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3
        assert all("id" in user for user in users)
        assert all("email" in user for user in users)
        assert all("user_name" in user for user in users)
        assert all("is_active" in user for user in users)

        # Verify no password is returned
        assert all("password" not in user for user in users)


@pytest.mark.integration
class TestCreateUserEndpoint:
    """Test POST /api/v1/users endpoint."""

    async def test_create_user_success(
        self, async_client: AsyncClient, sample_user_data
    ):
        """Test successfully creating a new user."""
        # Act
        response = await async_client.post("/api/v1/users", json=sample_user_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["user_name"] == sample_user_data["user_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data

    @pytest.mark.parametrize(
        "field, bad_value, expected_msg",
        [
            ("email", "", "Email cannot be empty"),
            ("email", "   ", "Email cannot be empty"),
            ("user_name", "", "Username cannot be empty"),
            ("user_name", "   ", "Username cannot be empty"),
        ],
    )
    async def test_create_user_validation_errors(
        self, async_client: AsyncClient, field: str, bad_value: str, expected_msg: str
    ):
        """Test various validation errors (empty/whitespace fields)."""
        # Arrange: Start with a valid base payload
        user_data = {
            "user_name": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }

        # Inject the bad value dynamically
        user_data[field] = bad_value

        # Act
        response = await async_client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert expected_msg in data["message"]

    async def test_create_user_duplicate_email(
        self, async_client: AsyncClient, created_user
    ):
        """Test creating a user with duplicate email returns 409."""
        # Arrange
        duplicate_user_data = {
            "user_name": "differentuser",
            "email": created_user["email"],  # Same email as existing user
            "password": "password123",
        }

        # Act
        response = await async_client.post("/api/v1/users", json=duplicate_user_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "message" in data
        assert "email" in data["message"].lower()
        assert "already exists" in data["message"].lower()

    async def test_create_multiple_users_different_emails(
        self, async_client: AsyncClient
    ):
        """Test creating multiple users with different emails succeeds."""
        # Arrange
        users_data = [
            {
                "user_name": f"user{i}",
                "email": f"user{i}@example.com",
                "password": f"password{i}",
            }
            for i in range(1, 4)
        ]

        # Act & Assert
        for user_data in users_data:
            response = await async_client.post("/api/v1/users", json=user_data)
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["user_name"] == user_data["user_name"]


@pytest.mark.integration
class TestGetUserByIdEndpoint:
    """Test GET /api/v1/users/{user_id} endpoint."""

    async def test_get_user_success(self, async_client: AsyncClient, created_user):
        """Test successfully retrieving a user by ID."""
        # Act
        response = await async_client.get(f"/api/v1/users/{created_user['id']}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["email"] == created_user["email"]
        assert data["user_name"] == created_user["user_name"]
        assert data["is_active"] == created_user["is_active"]
        assert "password" not in data

    async def test_get_user_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent user returns 404."""
        # Act
        response = await async_client.get("/api/v1/users/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "message" in data
        assert "not found" in data["message"].lower()

    async def test_get_user_invalid_id_format(self, async_client: AsyncClient):
        """Test getting a user with invalid ID format returns 422."""
        # Act
        response = await async_client.get("/api/v1/users/invalid")

        # Assert
        assert response.status_code == 422

    async def test_get_user_negative_id(self, async_client: AsyncClient):
        """Test getting a user with negative ID returns 404."""
        # Act
        response = await async_client.get("/api/v1/users/-1")

        # Assert
        assert response.status_code == 404

    async def test_get_each_created_user(
        self, async_client: AsyncClient, created_users
    ):
        """Test retrieving each user that was created."""
        # Act & Assert
        for user in created_users:
            response = await async_client.get(f"/api/v1/users/{user['id']}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user["id"]
            assert data["email"] == user["email"]


@pytest.mark.integration
class TestUserEndpointRequestID:
    """Test that request ID is present in responses."""

    async def test_create_user_has_request_id(
        self, async_client: AsyncClient, sample_user_data
    ):
        """Test that create user response includes X-Request-ID header."""
        # Act
        response = await async_client.post("/api/v1/users", json=sample_user_data)

        # Assert
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0

    async def test_list_users_has_request_id(self, async_client: AsyncClient):
        """Test that list users response includes X-Request-ID header."""
        # Act
        response = await async_client.get("/api/v1/users")

        # Assert
        assert "x-request-id" in response.headers

    async def test_get_user_has_request_id(
        self, async_client: AsyncClient, created_user
    ):
        """Test that get user response includes X-Request-ID header."""
        # Act
        response = await async_client.get(f"/api/v1/users/{created_user['id']}")

        # Assert
        assert "x-request-id" in response.headers
