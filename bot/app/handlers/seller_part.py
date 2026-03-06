from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import SellerPartStates
from app.keyboards.common import shop_menu, cancel_kb
from app.services.storage import get_seller

router = Router()

# Menyu tugmalari state ichida "model/nom" bo'lib ketmasligi uchun
MENU_WORDS = {
    "🏪 Mening do‘konim",
    "📦 Tovarlarim",
    "➕ Zapchast qo‘shish",
    "🔎 Qidiruv",
    "💬 Fikr bildiring",
    "🌍 Hudud",
    "⬅️ Bosh menyu",
}


# 1) Universal cancel/back (qaysi state bo'lishidan qat'i nazar ishlaydi)
@router.message(F.text.in_(["⬅️ Ortga", "❌ Bekor qilish"]))
async def cancel_any(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Do‘kon kabineti:", reply_markup=shop_menu())


# 2) Zapchast qo'shishni boshlash
@router.message(F.text == "➕ Zapchast qo‘shish")
async def part_start(message: Message, state: FSMContext):
    info = get_seller(message.from_user.id)
    if not info:
        await message.answer("Avval 🏪 Mening do‘konim orqali do‘kon yarating.", reply_markup=shop_menu())
        return

    await state.set_state(SellerPartStates.car_model)
    await message.answer(
        "Mashina modelini yozing (masalan: Cobalt):",
        reply_markup=cancel_kb()
    )


# 3) Car model qabul qilish (GUARD bilan)
@router.message(SellerPartStates.car_model, F.text)
async def part_car_model(message: Message, state: FSMContext):
    text = message.text.strip()

    # GUARD: user menyu tugmalarini bosib yuborsa, qabul qilmaymiz
    if text in MENU_WORDS:
        await message.answer(
            "Iltimos, mashina modelini yozing.\n"
            "Yoki ⬅️ Ortga / ❌ Bekor qilish ni bosing.",
            reply_markup=cancel_kb()
        )
        return

    await state.update_data(car_model=text)
    await state.set_state(SellerPartStates.part_name)
    await message.answer(
        "Zapchast nomini yozing (masalan: Old fara):",
        reply_markup=cancel_kb()
    )


# 4) Part name qabul qilish (GUARD bilan) va API ga yuborish
@router.message(SellerPartStates.part_name, F.text)
async def part_name(message: Message, state: FSMContext, api):
    text = message.text.strip()

    # GUARD
    if text in MENU_WORDS:
        await message.answer(
            "Iltimos, zapchast nomini yozing.\n"
            "Yoki ⬅️ Ortga / ❌ Bekor qilish ni bosing.",
            reply_markup=cancel_kb()
        )
        return

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