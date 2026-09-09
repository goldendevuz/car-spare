import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shop, Part
from ..schemas import PartCreate, PartUpdate, PartOut

router = APIRouter()


def require_seller_token(x_seller_token: str | None = Header(default=None, alias="X-SELLER-TOKEN")) -> str:
    if not x_seller_token:
        raise HTTPException(status_code=403, detail="X-SELLER-TOKEN header kerak")
    return x_seller_token


def get_shop_or_404(db: Session, shop_id: uuid.UUID) -> Shop:
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop topilmadi")
    return shop


def check_shop_token(shop: Shop, token: str):
    if str(shop.seller_token) != str(token):
        raise HTTPException(status_code=403, detail="Token noto'g'ri")


@router.post("/parts/create/", response_model=PartOut, status_code=201)
def create_part(
    payload: PartCreate,
    db: Session = Depends(get_db),
    token: str = Depends(require_seller_token),
):
    shop = get_shop_or_404(db, payload.shop)
    check_shop_token(shop, token)

    part = Part(
        shop_id=payload.shop,
        car_model=payload.car_model,
        name=payload.name,
        price=payload.price,
        in_stock=payload.in_stock,
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@router.get("/parts/{part_id}/", response_model=PartOut)
def get_part(part_id: uuid.UUID, db: Session = Depends(get_db)):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part topilmadi")
    return part


@router.patch("/parts/{part_id}/", response_model=PartOut)
def patch_part(
    part_id: uuid.UUID,
    payload: PartUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(require_seller_token),
):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part topilmadi")
    check_shop_token(part.shop, token)

    data = payload.model_dump(exclude_unset=True)
    if "shop" in data:
        part.shop_id = data.pop("shop")
    for field, value in data.items():
        setattr(part, field, value)

    db.commit()
    db.refresh(part)
    return part


@router.delete("/parts/{part_id}/")
def delete_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    token: str = Depends(require_seller_token),
):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part topilmadi")
    check_shop_token(part.shop, token)

    db.delete(part)
    db.commit()
    return {"detail": "Deleted"}


@router.get("/shops/{shop_id}/parts/seller/", response_model=list[PartOut])
def list_seller_parts(
    shop_id: uuid.UUID,
    db: Session = Depends(get_db),
    token: str = Depends(require_seller_token),
):
    shop = get_shop_or_404(db, shop_id)
    check_shop_token(shop, token)

    parts = (
        db.query(Part)
        .filter(Part.shop_id == shop_id)
        .order_by(Part.created_at.desc())
        .all()
    )
    return parts
