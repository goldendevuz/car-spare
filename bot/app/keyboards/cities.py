from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def cities_kb(cities: list[dict], prefix: str = "city", selected_id: int | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in cities:
        text = f"✅ {c['name']}" if selected_id == c["id"] else c["name"]
        kb.button(text=text, callback_data=f"{prefix}:{c['id']}")
    kb.adjust(2)
    return kb.as_markup()