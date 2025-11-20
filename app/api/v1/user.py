from fastapi import APIRouter, Depends 

from app.api.deps import get_user_service
from app.services.user_service import UserService
from app.models.users import UserRead, UserCreate

router = APIRouter()

@router.get("/users", response_model=list[UserRead])
def list_users(service: UserService = Depends(get_user_service)):
    users = service.list_users()
    return users

@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    new_user = service.create_user(email=user.email, user_name=user.username)
    return new_user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user