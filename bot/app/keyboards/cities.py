from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def cities_kb(cities: list[dict], prefix: str = "city") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in cities:
        kb.button(text=c["name"], callback_data=f"{prefix}:{c['id']}")
    kb.adjust(2)
    return kb.as_markup()