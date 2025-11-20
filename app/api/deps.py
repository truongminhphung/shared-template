from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import UserService

def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session)