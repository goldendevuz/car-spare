import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    car_model: str = Field(min_length=3)
    name: str = Field(min_length=3)
    price: Optional[int] = None
    in_stock: bool = True

    @field_validator("car_model", "name")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("kamida 3 ta belgidan iborat bo'lishi kerak")
        return v


class PartUpdate(BaseModel):
    shop: Optional[int] = None
    car_model: Optional[str] = Field(default=None, min_length=3)
    name: Optional[str] = Field(default=None, min_length=3)
    price: Optional[int] = None
    in_stock: Optional[bool] = None

    @field_validator("car_model", "name")
    @classmethod
    def strip_and_check(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("kamida 3 ta belgidan iborat bo'lishi kerak")
        return v


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
