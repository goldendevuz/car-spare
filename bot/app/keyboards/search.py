from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def map_kb(shop_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗺 Xaritada ko‘rish", callback_data=f"map:{shop_id}")
    return kb.as_markup()


def search_page_kb(page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Oldingi", callback_data=f"s:page:{max(page-1, 1)}")
    kb.button(text=f"{page}/{max(total_pages, 1)}", callback_data="s:noop")
    kb.button(text="Keyingi ➡️", callback_data=f"s:page:{min(page+1, total_pages)}")
    kb.adjust(3)
    return kb.as_markup()