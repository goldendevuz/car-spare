from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Qidiruv")],
            [KeyboardButton(text="🏪 Mening do‘konim")],
            [KeyboardButton(text="💬 Fikr bildiring"), KeyboardButton(text="🌍 Hudud")],
        ],
        resize_keyboard=True
    )


def shop_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Zapchast qo‘shish")],
            [KeyboardButton(text="📦 Tovarlarim")],
            [KeyboardButton(text="⬅️ Bosh menyu")],
        ],
        resize_keyboard=True
    )


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True
    )


def location_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )


# ---------- Inline keyboards for products ----------
def products_kb(page: int, total_pages: int, items: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for p in items:
        title = f"{p['car_model']} — {p['name']}"
        kb.button(text=title, callback_data=f"prod:item:{p['id']}")

    kb.adjust(1)

    nav = InlineKeyboardBuilder()
    nav.button(text="⬅️ Orqaga", callback_data=f"prod:page:{max(page-1, 0)}")
    nav.button(text=f"{page+1}/{max(total_pages, 1)}", callback_data="prod:noop")
    nav.button(text="Keyingi ➡️", callback_data=f"prod:page:{min(page+1, max(total_pages-1, 0))}")
    nav.adjust(3)

    kb.attach(nav)
    return kb.as_markup()


def product_detail_kb(part_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Tahrirlash", callback_data=f"prod:edit:{part_id}")
    kb.button(text="🗑 O‘chirish", callback_data=f"prod:del:{part_id}")
    kb.button(text="⬅️ Ro‘yxatga qaytish", callback_data="prod:back")
    kb.adjust(1)
    return kb.as_markup()