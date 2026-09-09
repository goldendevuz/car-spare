from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shop, City
from ..schemas import ShopCreate, ShopOut

router = APIRouter()


@router.post("/shops/create/", response_model=ShopOut, status_code=201)
def create_shop(payload: ShopCreate, db: Session = Depends(get_db)):
    city = db.get(City, payload.city)
    if not city:
        raise HTTPException(status_code=400, detail="City topilmadi")

    shop = Shop(
        name=payload.name,
        phone=payload.phone,
        city_id=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        landmark=payload.landmark,
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


@router.get("/shops/{shop_id}/", response_model=ShopOut)
def get_shop(shop_id: int, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Do'kon topilmadi")
    return shop
