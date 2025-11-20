from pydantic import BaseModel

class OrderCreate(BaseModel):
    item_name: str
    quantity: int
    user_id: int

class OrderRead(BaseModel):
    id: int
    item_name: str
    quantity: int
    user_id: int

    class Config:
        orm_mode = True