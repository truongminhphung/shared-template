import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.tables.users import User
from app.core.exceptions import ResourceNotFound, DuplicateResource

logger = logging.getLogger(__name__)

class UserService:
    """
    Business logic service for user operations.
    
    Handles CRUD operations on users with async database interactions.
    Validates data and raises appropriate exceptions for error cases.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def list_users(self) -> list[User]:
        """Retrieve all users from the database."""
        result = await self.session.execute(select(User))
        return result.scalars().all()
    
    async def get_user(self, user_id: int) -> User:
        """
        Retrieve a user by ID.
        
        Raises:
            ResourceNotFound: If user does not exist.
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User not found with ID: {user_id}")
            raise ResourceNotFound("User", user_id)
        logger.info(f"Retrieved user with ID: {user_id}")
        return user
    
    
    async def create_user(self, email: str, user_name: str) -> User:
        """
        Create a new user.
        
        Raises:
            DuplicateResource: If email already exists.
        """
        # check if user with email already exists
        result = await self.session.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            logger.warning(f"Attempt to create duplicate user with email: {email}")
            raise DuplicateResource("User", "email", email)

        new_user = User(email=email, user_name=user_name)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        logger.info(f"Created new user with email: {email}")
        return new_user
    