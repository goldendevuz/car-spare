import json
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parents[2]  # bot/
FILE_PATH = BASE_DIR / "seller_tokens.json"


def _load() -> Dict[str, Any]:
    if not FILE_PATH.exists():
        return {}
    try:
        return json.loads(FILE_PATH.read_text(encoding="utf-8") or "{}")
    except Exception:
        return {}


def _save(data: Dict[str, Any]) -> None:
    FILE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def set_seller(telegram_id: int, shop_id: int, seller_token: str) -> None:
    data = _load()
    rec = data.get(str(telegram_id), {})
    rec.update({"shop_id": shop_id, "seller_token": seller_token})
    data[str(telegram_id)] = rec
    _save(data)


def get_seller(telegram_id: int) -> Optional[Dict[str, Any]]:
    data = _load()
    rec = data.get(str(telegram_id))
    return rec if rec else None


def delete_seller(telegram_id: int) -> None:
    data = _load()
    data.pop(str(telegram_id), None)
    _save(data)


def set_last_city(telegram_id: int, city_id: int) -> None:
    data = _load()
    rec = data.get(str(telegram_id), {})
    rec["last_city_id"] = city_id
    data[str(telegram_id)] = rec
    _save(data)


def get_last_city(telegram_id: int) -> Optional[int]:
    data = _load()
    rec = data.get(str(telegram_id)) or {}
    val = rec.get("last_city_id")
    return int(val) if val is not None else None


def get_role(telegram_id: int) -> str:
    """
    Agar telegram_id storage'da shop_id/seller_token bo'lsa -> seller
    Aks holda -> user
    """
    rec = get_seller(telegram_id)
    if rec and rec.get("shop_id") and rec.get("seller_token"):
        return "seller"
    return "user"