from pydantic import BaseModel, ConfigDict

class OrderCreate(BaseModel):
    item_name: str
    quantity: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class OrderRead(BaseModel):
    id: int
    item_name: str
    quantity: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)