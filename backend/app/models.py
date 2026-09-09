import uuid

from sqlalchemy import (
    Column, BigInteger, Integer, String, Boolean, Float, ForeignKey, DateTime, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


def uuid_pk():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class City(Base):
    __tablename__ = "cities"

    id = uuid_pk()
    name = Column(String(80), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    shops = relationship("Shop", back_populates="city")
    districts = relationship("District", back_populates="city")

    def __repr__(self):
        return self.name


class District(Base):
    __tablename__ = "districts"

    id = uuid_pk()
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    city = relationship("City", back_populates="districts")

    name = Column(String(120), nullable=False)
    soato_code = Column(String(20), nullable=True)

    settlements = relationship("Settlement", back_populates="district")

    def __repr__(self):
        return self.name


class Settlement(Base):
    __tablename__ = "settlements"

    TYPE_CITY = "shahar"
    TYPE_VILLAGE = "qishloq"

    id = uuid_pk()
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=False)
    district = relationship("District", back_populates="settlements")

    name = Column(String(120), nullable=False)
    type = Column(String(20), default=TYPE_VILLAGE, nullable=False)
    soato_code = Column(String(20), nullable=True)

    def __repr__(self):
        return self.name


class Shop(Base):
    __tablename__ = "shops"

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"

    id = uuid_pk()
    name = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)

    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    city = relationship("City", back_populates="shops")

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    landmark = Column(String(255), default="", nullable=False)

    status = Column(String(20), default=STATUS_PENDING, nullable=False)

    seller_token = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    parts = relationship("Part", back_populates="shop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"


class Part(Base):
    __tablename__ = "parts"

    id = uuid_pk()
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    shop = relationship("Shop", back_populates="parts")

    car_model = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=True)
    in_stock = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.car_model} - {self.name}"


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = uuid_pk()
    telegram_id = Column(BigInteger, nullable=False)
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    city = relationship("City")

    query_text = Column(String(255), nullable=False)
    normalized_query = Column(String(255), default="")

    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchResultLog(Base):
    __tablename__ = "search_result_logs"

    id = uuid_pk()
    search_log_id = Column(UUID(as_uuid=True), ForeignKey("search_logs.id", ondelete="CASCADE"), nullable=False)
    search_log = relationship("SearchLog")

    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    shop = relationship("Shop")

    rank = Column(Integer, nullable=False)
    best_part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id", ondelete="SET NULL"), nullable=True)
    score = Column(Float, default=0.0)


class Feedback(Base):
    __tablename__ = "feedbacks"

    ROLE_USER = "user"
    ROLE_SELLER = "seller"

    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_RESOLVED = "resolved"

    id = uuid_pk()
    telegram_id = Column(BigInteger, nullable=False)
    role = Column(String(10), default=ROLE_USER, nullable=False)

    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=True)
    city = relationship("City")

    message = Column(Text, nullable=False)

    status = Column(String(20), default=STATUS_NEW, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
