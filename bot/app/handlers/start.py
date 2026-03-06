from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from ..keyboards.common import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    text = (
        "<b>ZapchastTOP botiga xush kelibsiz 🚗</b>\n\n"
        "🔎 <b>Qidiruv</b> — <u>zapchast qidiring</u>\n"
        "🏪 <b>Mening do‘konim</b> — sotuvchilar uchun kabinet\n"
        "💬 <b>Fikr bildiring</b> — taklif yoki shikoyat yuboring"
    )

    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")