from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from ..models import City
from ..schemas import CityOut

router = APIRouter()


@router.get("/cities/", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    cities = db.scalars(
        select(City).where(City.is_active.is_(True)).order_by(City.name)
    ).all()
    return cities
