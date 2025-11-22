from fastapi import APIRouter, Depends
import logging

from app.api.deps import get_user_service
from app.services.user_service import UserService
from app.models.users import UserRead, UserCreate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/users", response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_user_service)):
    logger.info("Listing users")
    users = await service.list_users()
    logger.info(f"Retrieved {len(users)} users")
    return users

@router.post("/users", response_model=UserRead)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    new_user = await service.create_user(email=user.email, user_name=user.user_name)
    return new_user

@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = await service.get_user(user_id)
    return user