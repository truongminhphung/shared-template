from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    is_active: bool