from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    user_name: str
    email: str
    password: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_name: str
    email: str
    is_active: bool