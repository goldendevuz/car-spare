from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import FeedbackStates
from ..keyboards.common import main_menu
from ..services.storage import get_role, get_last_city

router = Router()


@router.message(F.text == "💬 Fikr bildiring")
async def feedback_start(message: Message, state: FSMContext):
    await state.set_state(FeedbackStates.waiting_text)
    await message.answer("Fikringizni yozib yuboring (taklif/shikoyat):", reply_markup=main_menu())


@router.message(FeedbackStates.waiting_text, F.text)
async def feedback_send(message: Message, state: FSMContext, api):
    text = message.text.strip()
    role = get_role(message.from_user.id)
    city_id = get_last_city(message.from_user.id)  # bo'lsa bog'lab qo'yamiz

    try:
        api.create_feedback(
            telegram_id=message.from_user.id,
            role=role,
            message=text,
            city_id=city_id,
        )
    except Exception as e:
        await message.answer(f"❌ Feedback yuborishda xato: {e}", reply_markup=main_menu())
        await state.clear()
        return

    await message.answer("✅ Rahmat! Fikringiz qabul qilindi.", reply_markup=main_menu())
    await state.clear()