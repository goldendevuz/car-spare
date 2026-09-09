import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import City, Shop, Part, SearchLog, SearchResultLog
from ..schemas import SearchResponse
from ..search_logic import build_query_variants, detect_model_anywhere, normalize_query

router = APIRouter()


@router.get("/search/", response_model=SearchResponse)
def search(
    db: Session = Depends(get_db),
    q: str = Query(...),
    city_id: uuid.UUID = Query(...),
    telegram_id: int = Query(...),
    page: int = Query(1),
    page_size: int = Query(3),
):
    q = (q or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="q, city_id, telegram_id are required")

    city = db.query(City).filter(City.id == city_id, City.is_active.is_(True)).first()
    if not city:
        raise HTTPException(status_code=404, detail="City topilmadi")

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 20:
        page_size = 3

    nq = normalize_query(q)

    active_shop_ids = db.query(Shop.id).filter(
        Shop.status == Shop.STATUS_ACTIVE, Shop.city_id == city_id
    )

    forced_model_token, remaining_query, model_conf = detect_model_anywhere(nq)

    detected_model = None
    detected_model_sim = 0.0

    if forced_model_token:
        db_model = (
            db.query(Part.car_model)
            .filter(Part.shop_id.in_(active_shop_ids))
            .filter(func.lower(Part.car_model) == forced_model_token.lower())
            .first()
        )
        if db_model:
            detected_model = db_model[0]
            detected_model_sim = model_conf
        else:
            log = SearchLog(
                telegram_id=telegram_id,
                city_id=city_id,
                query_text=q,
                normalized_query=nq,
                results_count=0,
            )
            db.add(log)
            db.commit()
            return SearchResponse(
                count=0,
                page=page,
                page_size=page_size,
                results=[],
                model_detected=forced_model_token,
                model_detected_sim=round(model_conf, 3),
                hint=f"Bu hududda '{forced_model_token.title()}' bo'yicha zapchast topilmadi.",
            )

    search_text = remaining_query if (detected_model and remaining_query) else nq

    parts_qs = db.query(Part).filter(Part.shop_id.in_(active_shop_ids), Part.in_stock.is_(True))
    if detected_model:
        parts_qs = parts_qs.filter(func.lower(Part.car_model) == detected_model.lower())

    variants = build_query_variants(search_text)
    full_text_lower = func.lower(func.concat(Part.car_model, " ", Part.name))

    def variant_score(v: str):
        v_lower = v.lower()
        starts = case((full_text_lower.startswith(v_lower), 1.0), else_=0.0)
        contains = case((full_text_lower.contains(v_lower), 0.6), else_=0.0)
        fuzzy = func.similarity(full_text_lower, v_lower)
        return func.greatest(starts, contains, fuzzy)

    score_exprs = [variant_score(v) for v in variants]
    score = score_exprs[0]
    for expr in score_exprs[1:]:
        score = func.greatest(score, expr)

    parts = (
        parts_qs.add_columns(score.label("score"))
        .filter(score > 0.10)
        .order_by(score.desc())
        .limit(1200)
        .all()
    )

    best = {}
    for part, part_score in parts:
        sid = part.shop_id
        if sid not in best or part_score > best[sid]["score"]:
            shop = part.shop
            best[sid] = {
                "shop_id": part.shop_id,
                "shop_name": shop.name,
                "phone": shop.phone,
                "landmark": shop.landmark,
                "latitude": shop.latitude,
                "longitude": shop.longitude,
                "best_part_id": part.id,
                "best_part": f"{part.car_model} — {part.name}",
                "score": float(part_score),
            }

    results_all = sorted(best.values(), key=lambda x: x["score"], reverse=True)
    count = len(results_all)

    start = (page - 1) * page_size
    end = start + page_size
    results_page = results_all[start:end]

    log = SearchLog(
        telegram_id=telegram_id,
        city_id=city_id,
        query_text=q,
        normalized_query=nq,
        results_count=count,
    )
    db.add(log)
    db.flush()

    for idx, r in enumerate(results_all[:20], start=1):
        db.add(SearchResultLog(
            search_log_id=log.id,
            shop_id=r["shop_id"],
            rank=idx,
            best_part_id=r.get("best_part_id"),
            score=r["score"],
        ))
    db.commit()

    return SearchResponse(
        count=count,
        page=page,
        page_size=page_size,
        results=results_page,
        model_detected=detected_model,
        model_detected_sim=round(detected_model_sim, 3),
    )
