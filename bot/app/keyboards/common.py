from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔎 Qidiruv", callback_data="nav:search")
    kb.button(text="🏪 Mening do‘konim", callback_data="nav:myshop")
    kb.button(text="💬 Fikr bildiring", callback_data="nav:feedback")
    kb.button(text="🌍 Hudud", callback_data="nav:hudud")
    kb.adjust(1, 1, 2)
    return kb.as_markup()


def shop_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Zapchast qo‘shish", callback_data="shop:add_part")
    kb.button(text="📦 Tovarlarim", callback_data="shop:products")
    kb.button(text="⬅️ Bosh menyu", callback_data="nav:main")
    kb.adjust(1)
    return kb.as_markup()


def cancel_inline_kb(target: str) -> InlineKeyboardMarkup:
    """target: nima uchun bekor qilinsa qayerga qaytish kerakligi (cancel:<target>)."""
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Bekor qilish", callback_data=f"cancel:{target}")
    return kb.as_markup()


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ---------- Inline keyboards for products ----------
def products_kb(page: int, total_pages: int, items: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for p in items:
        title = f"{p['car_model']} — {p['name']}"
        kb.button(text=title, callback_data=f"prod:item:{p['id']}")

    kb.adjust(1)

    if total_pages > 1:
        nav = InlineKeyboardBuilder()
        nav.button(text="⬅️ Orqaga", callback_data=f"prod:page:{max(page-1, 0)}")
        nav.button(text=f"{page+1}/{total_pages}", callback_data="prod:noop")
        nav.button(text="Keyingi ➡️", callback_data=f"prod:page:{min(page+1, total_pages-1)}")
        nav.adjust(3)
        kb.attach(nav)

    back = InlineKeyboardBuilder()
    back.button(text="⬅️ Bosh menyu", callback_data="nav:main")
    kb.attach(back)

    return kb.as_markup()


def product_detail_kb(part_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Tahrirlash", callback_data=f"prod:edit:{part_id}")
    kb.button(text="🗑 O‘chirish", callback_data=f"prod:del:{part_id}")
    kb.button(text="⬅️ Ro‘yxatga qaytish", callback_data="prod:back")
    kb.adjust(1)
    return kb.as_markup()
