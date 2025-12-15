from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4)

class UserResponse(BaseModel):
    id: int
    username: str

    # Ця магія дозволяє Pydantic читати дані прямо з об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class DishBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None
    price: float = Field(gt=0)

class DishCreate(DishBase):
    category_id: int


class DishResponse(DishBase):
    id: int
    image_url: Optional[str] = None
    category_id: int

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)

class CategoryResponse(BaseModel):
    id: int
    name: str

    dishes: List[DishResponse]

    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int = Field(gt=0, default=1)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    dish_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

