from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Feedback
from ..schemas import FeedbackCreate, FeedbackOut

router = APIRouter()


@router.post("/feedback/", response_model=FeedbackOut, status_code=201)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    fb = Feedback(
        telegram_id=payload.telegram_id,
        role=payload.role,
        city_id=payload.city,
        message=payload.message,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
