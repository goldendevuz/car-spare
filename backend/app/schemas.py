import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ShopCreate(BaseModel):
    name: str
    phone: str
    city: int
    latitude: float
    longitude: float
    landmark: str = ""


class ShopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    city_id: int
    latitude: float
    longitude: float
    landmark: str
    status: str
    seller_token: uuid.UUID


class PartCreate(BaseModel):
    shop: int
    car_model: str
    name: str
    price: Optional[int] = None
    in_stock: bool = True


class PartUpdate(BaseModel):
    shop: Optional[int] = None
    car_model: Optional[str] = None
    name: Optional[str] = None
    price: Optional[int] = None
    in_stock: Optional[bool] = None


class PartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    shop_id: int
    car_model: str
    name: str
    price: Optional[int]
    in_stock: bool
    created_at: datetime


class FeedbackCreate(BaseModel):
    telegram_id: int
    role: str = "user"
    city: Optional[int] = None
    message: str


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    telegram_id: int
    role: str
    city_id: Optional[int]
    message: str
    status: str
    created_at: datetime


class SearchResultItem(BaseModel):
    shop_id: int
    shop_name: str
    phone: str
    landmark: str
    latitude: float
    longitude: float
    best_part_id: int
    best_part: str
    score: float


class SearchResponse(BaseModel):
    count: int
    page: int
    page_size: int
    results: List[SearchResultItem]
    model_detected: Optional[str] = None
    model_detected_sim: float = 0.0
    hint: Optional[str] = None
