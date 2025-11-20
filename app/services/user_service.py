from sqlalchemy.orm import Session
from app.db.tables.users import User
from app.core.exceptions import ResourceNotFound, DuplicateResource

class UserService:
    def __init__(self, session: Session):
        self.session = session
    
    def list_users(self) -> list[User]:
        return self.session.query(User).all()
    
    def get_user(self, user_id: int) -> User | None:
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFound("User", user_id)
        return user
    
    
    def create_user(self, email: str, user_name: str) -> User:
        # check if user with email already exists
        existing_user = self.session.query(User).filter(User.email == email).first()
        if existing_user:
            raise DuplicateResource("User", "email", email)

        new_user = User(email=email, user_name=user_name)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user
    