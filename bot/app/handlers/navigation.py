from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.common import main_menu, shop_menu, phone_kb
from ..keyboards.cities import cities_kb
from ..states import SellerShopStates, SearchStates, FeedbackStates
from ..services.storage import get_seller, delete_seller, set_last_city, get_role, get_last_city

router = Router()


@router.message(F.text == "⬅️ Bosh menyu")
async def nav_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu", reply_markup=main_menu())


@router.message(F.text == "🏪 Mening do‘konim")
async def nav_my_shop(message: Message, state: FSMContext, api):
    await state.clear()

    info = get_seller(message.from_user.id)
    if info and not api.shop_exists(info["shop_id"]):
        delete_seller(message.from_user.id)
        info = None

    if info:
        await message.answer("Do‘kon kabineti:", reply_markup=shop_menu())
        return

    # ✅ Do'kon yo'q bo'lsa: darhol registratsiya boshlanadi
    await state.set_state(SellerShopStates.phone)
    await message.answer("Do‘kon yaratish uchun telefon raqamingizni yuboring:", reply_markup=phone_kb())


@router.message(F.text == "🔎 Qidiruv")
async def nav_search(message: Message, state: FSMContext, api):
    await state.clear()

    try:
        cities = api.list_cities()
    except Exception as e:
        await message.answer(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        return

    if not cities:
        await message.answer("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        return

    await state.set_state(SearchStates.city)
    await message.answer("Qaysi hudud (shahar)da qidiramiz?", reply_markup=cities_kb(cities, prefix="city"))


@router.message(F.text == "💬 Fikr bildiring")
async def nav_feedback(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FeedbackStates.waiting_text)
    await message.answer("Fikringizni yozib yuboring (taklif/shikoyat):", reply_markup=main_menu())


@router.message(F.text == "🌍 Hudud")
async def nav_city(message: Message, state: FSMContext, api):
    await state.clear()

    try:
        cities = api.list_cities()
    except Exception as e:
        await message.answer(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        return

    if not cities:
        await message.answer("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        return

    await message.answer("Hududni tanlang:", reply_markup=cities_kb(cities, prefix="setcity"))


@router.callback_query(F.data.startswith("setcity:"))
async def set_city(cb: CallbackQuery):
    city_id = int(cb.data.split(":")[1])
    set_last_city(cb.from_user.id, city_id)
    await cb.message.answer("✅ Hudud saqlandi.", reply_markup=main_menu())
    await cb.answer()