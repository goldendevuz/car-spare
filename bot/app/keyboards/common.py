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
