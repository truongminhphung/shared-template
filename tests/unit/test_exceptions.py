"""Unit tests for custom exception handlers."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.core.exceptions import (
    ResourceNotFound,
    DuplicateResource,
    ValidationError,
)
from app.core.handlers import (
    resource_not_found_handler,
    duplicate_resource_handler,
    validation_error_handler,
)


@pytest.mark.unit
class TestResourceNotFoundHandler:
    """Test ResourceNotFoundError exception handler."""

    async def test_handler_returns_404_status(self):
        """Test handler returns 404 status code."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ResourceNotFound, resource_not_found_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise ResourceNotFound(entity_name="User", entity_id=123)
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        assert response.status_code == 404

    async def test_handler_response_structure(self):
        """Test handler returns correct JSON structure."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ResourceNotFound, resource_not_found_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise ResourceNotFound(entity_name="User", entity_id=456)
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        data = response.json()
        assert "message" in data
        assert "User" in data["message"]
        assert "456" in data["message"]
        assert "not found" in data["message"].lower()

    async def test_handler_with_different_resource_types(self):
        """Test handler works with different resource types."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ResourceNotFound, resource_not_found_handler)
        
        @app.get("/test/{resource_type}/{resource_id}")
        async def test_endpoint(resource_type: str, resource_id: int):
            raise ResourceNotFound(
                entity_name=resource_type,
                entity_id=resource_id
            )
        
        # Act & Assert
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Test User
            response = await client.get("/test/User/123")
            assert response.status_code == 404
            assert "User" in response.json()["message"]
            
            # Test Order
            response = await client.get("/test/Order/789")
            assert response.status_code == 404
            assert "Order" in response.json()["message"]


@pytest.mark.unit
class TestDuplicateResourceHandler:
    """Test DuplicateResourceError exception handler."""

    async def test_handler_returns_409_status(self):
        """Test handler returns 409 Conflict status code."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(DuplicateResource, duplicate_resource_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise DuplicateResource(
                entity_name="User",
                field_name="email",
                field_value="test@example.com"
            )
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        assert response.status_code == 409

    async def test_handler_response_structure(self):
        """Test handler returns correct JSON structure."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(DuplicateResource, duplicate_resource_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise DuplicateResource(
                entity_name="User",
                field_name="email",
                field_value="duplicate@example.com"
            )
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        data = response.json()
        assert "message" in data
        assert "User" in data["message"]
        assert "email" in data["message"]
        assert "duplicate@example.com" in data["message"]
        assert "already exists" in data["message"].lower()

    async def test_handler_with_different_fields(self):
        """Test handler works with different field names."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(DuplicateResource, duplicate_resource_handler)
        
        @app.get("/test/{field}")
        async def test_endpoint(field: str):
            raise DuplicateResource(
                entity_name="User",
                field_name=field,
                field_value="testvalue"
            )
        
        # Act & Assert
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Test email field
            response = await client.get("/test/email")
            assert response.status_code == 409
            assert "email" in response.json()["message"]
            
            # Test username field
            response = await client.get("/test/username")
            assert response.status_code == 409
            assert "username" in response.json()["message"]


@pytest.mark.unit
class TestValidationErrorHandler:
    """Test ValidationError exception handler."""

    async def test_handler_returns_400_status(self):
        """Test handler returns 400 Bad Request status code."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ValidationError, validation_error_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValidationError(field="email", message="Email cannot be empty")
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        assert response.status_code == 400

    async def test_handler_response_structure(self):
        """Test handler returns correct JSON structure."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ValidationError, validation_error_handler)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValidationError(
                field="username",
                message="Username must be at least 3 characters"
            )
        
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        # Assert
        data = response.json()
        assert "message" in data
        assert data["message"] == "Username must be at least 3 characters"

    @pytest.mark.parametrize("exception_instance, expected_message", [
        (
            ValidationError(field="email", message="Email cannot be empty"),
            "Email cannot be empty"
        ),
        (
            ValidationError(field="username", message="Username cannot be empty"),
            "Username cannot be empty"
        ),
        (
            ValidationError(field="email", message="Invalid email format"),
            "Invalid email format"
        ),
    ])
    async def test_handler_variations(
            self,
            exception_instance: ValidationError,
            expected_message: str
    ):
        """Test handler works with different validation error messages."""
        # Arrange
        app = FastAPI()
        app.add_exception_handler(ValidationError, validation_error_handler)

        @app.get("/test")
        async def test_endpoint():
            raise exception_instance
        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/test")
        
        assert response.status_code == 400
        assert response.json()["message"] == expected_message


@pytest.mark.unit
class TestExceptionAttributes:
    """Test custom exception attributes."""

    def test_resource_not_found_attributes(self):
        """Test ResourceNotFound has correct attributes."""
        # Act
        exception = ResourceNotFound(entity_name="User", entity_id=123)
        
        # Assert
        assert exception.entity_name == "User"
        assert exception.entity_id == 123

    def test_duplicate_resource_attributes(self):
        """Test DuplicateResource has correct attributes."""
        # Act
        exception = DuplicateResource(
            entity_name="User",
            field_name="email",
            field_value="test@example.com"
        )
        
        # Assert
        assert exception.entity_name == "User"
        assert exception.field_name == "email"
        assert exception.field_value == "test@example.com"

    def test_validation_error_attributes(self):
        """Test ValidationError has correct attributes."""
        # Act
        exception = ValidationError(
            field="username",
            message="Username is required"
        )
        
        # Assert
        assert exception.field == "username"
        assert exception.message == "Username is required"
