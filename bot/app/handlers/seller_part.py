from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states import SellerPartStates
from app.keyboards.common import shop_menu, cancel_inline_kb
from app.services.storage import get_seller

router = Router()


@router.callback_query(F.data == "shop:add_part")
async def part_start(cb: CallbackQuery, state: FSMContext):
    info = get_seller(cb.from_user.id)
    if not info:
        await cb.message.edit_text("Avval 🏪 Mening do‘konim orqali do‘kon yarating.", reply_markup=shop_menu())
        await cb.answer()
        return

    await state.set_state(SellerPartStates.car_model)
    await cb.message.edit_text(
        "Mashina modelini yozing (masalan: Cobalt):",
        reply_markup=cancel_inline_kb("part"),
    )
    await cb.answer()


@router.message(SellerPartStates.car_model, F.text)
async def part_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text.strip())
    await state.set_state(SellerPartStates.part_name)
    await message.answer(
        "Zapchast nomini yozing (masalan: Old fara):",
        reply_markup=cancel_inline_kb("part"),
    )


@router.message(SellerPartStates.part_name, F.text)
async def part_name(message: Message, state: FSMContext, api):
    text = message.text.strip()

    info = get_seller(message.from_user.id)
    if not info:
        await message.answer("Token topilmadi. Qayta /start qiling.", reply_markup=shop_menu())
        await state.clear()
        return

    data = await state.get_data()
    payload = {
        "shop": info["shop_id"],
        "car_model": data["car_model"],
        "name": text,
        "price": None,
        "in_stock": True,
    }

    try:
        part = api.create_part(payload, seller_token=info["seller_token"])
    except Exception as e:
        await message.answer(f"❌ API xatolik (zapchast qo‘shish): {e}", reply_markup=shop_menu())
        await state.clear()
        return

    await message.answer(
        f"✅ Qo‘shildi!\n{part['car_model']} — {part['name']}",
        reply_markup=shop_menu()
    )
    await state.clear()
