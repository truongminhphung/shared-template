import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.tables.users import User
from app.core.exceptions import ResourceNotFound, DuplicateResource, ValidationError


class UserService:
    """
    Business logic service for user operations.

    Handles CRUD operations on users with async database interactions.
    Validates data and raises appropriate exceptions for error cases.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def list_users(self) -> list[User]:
        """Retrieve all users from the database."""
        result = await self.session.execute(select(User))
        users = result.scalars().all()
        self.logger.info(f"Retrieved {len(users)} users")
        return users

    async def get_user(self, user_id: int) -> User:
        """
        Retrieve a user by ID.

        Raises:
            ResourceNotFound: If user does not exist.
        """
        self.logger.info(f"Fetching user with ID: {user_id}")
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            self.logger.error(f"User not found with ID: {user_id}")
            raise ResourceNotFound("User", user_id)
        self.logger.info(f"Retrieved user with ID: {user_id}")
        return user

    async def create_user(self, email: str, user_name: str) -> User:
        """
        Create a new user.
        Raises:
            ValidationError: If email or user_name is invalid.
            DuplicateResource: If email already exists.
        """
        # Validate email
        if not email or not email.strip():
            self.logger.warning("Attempt to create user with empty email")
            raise ValidationError("email", "Email cannot be empty")

        # Validate user_name
        if not user_name or not user_name.strip():
            self.logger.warning("Attempt to create user with empty user_name")
            raise ValidationError("user_name", "Username cannot be empty")

        # check if user with email already exists
        result = await self.session.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            self.logger.warning(f"Attempt to create duplicate user with email: {email}")
            raise DuplicateResource("User", "email", email)

        new_user = User(email=email, user_name=user_name)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        self.logger.info(f"Created new user with email: {email}")
        return new_user
