from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from ..keyboards.common import main_menu, remove_kb

router = Router()

MAIN_MENU_TEXT = (
    "<b>ZapchastTOP botiga xush kelibsiz 🚗</b>\n\n"
    "🔎 <b>Qidiruv</b> — <u>zapchast qidiring</u>\n"
    "🏪 <b>Mening do‘konim</b> — sotuvchilar uchun kabinet\n"
    "💬 <b>Fikr bildiring</b> — taklif yoki shikoyat yuboring"
)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    # eski reply-keyboard (agar bo'lsa) tozalanadi
    placeholder = await message.answer("⏳", reply_markup=remove_kb())
    await placeholder.delete()
    await message.answer(MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")