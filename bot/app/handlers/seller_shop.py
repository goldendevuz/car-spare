from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..states import SellerShopStates
from ..keyboards.common import phone_kb, location_kb, main_menu, shop_menu
from ..keyboards.cities import cities_kb
from ..services.storage import set_seller, get_seller, delete_seller

router = Router()


@router.message(F.text == "⬅️ Bosh menyu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu", reply_markup=main_menu())


@router.message(F.text == "🏪 Mening do‘konim")
async def my_shop(message: Message, state: FSMContext, api):
    info = get_seller(message.from_user.id)

    # agar local storage bor-u, lekin backendda shop yo'q bo'lsa -> reset
    if info and not api.shop_exists(info["shop_id"]):
        delete_seller(message.from_user.id)
        info = None

    if info:
        await message.answer("<u>Do‘kon kabineti:</u>", reply_markup=shop_menu(), parse_mode="HTML")
        return

    await state.set_state(SellerShopStates.phone)
    await message.answer("Do‘kon yaratish uchun telefon raqamingizni yuboring:", reply_markup=phone_kb())


@router.message(SellerShopStates.phone, F.contact)
async def shop_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    await state.set_state(SellerShopStates.name)
    await message.answer("Do‘kon nomini kiriting:", reply_markup=main_menu())


@router.message(SellerShopStates.name, F.text)
async def shop_name(message: Message, state: FSMContext, api):
    await state.update_data(name=message.text.strip())

    try:
        cities = api.list_cities()
    except Exception as e:
        await message.answer(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        await state.clear()
        return

    if not cities:
        await message.answer("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        await state.clear()
        return

    await state.set_state(SellerShopStates.city)
    await message.answer("Hudud (shahar)ni tanlang:", reply_markup=cities_kb(cities))


@router.callback_query(SellerShopStates.city, F.data.startswith("city:"))
async def shop_city_selected(cb: CallbackQuery, state: FSMContext):
    city_id = int(cb.data.split(":")[1])
    await state.update_data(city=city_id)

    await state.set_state(SellerShopStates.location)
    await cb.message.answer("Do‘kon lokatsiyasini yuboring:", reply_markup=location_kb())
    await cb.answer()


@router.message(SellerShopStates.location, F.location)
async def shop_location(message: Message, state: FSMContext):
    loc = message.location
    await state.update_data(latitude=loc.latitude, longitude=loc.longitude)

    await state.set_state(SellerShopStates.landmark)
    await message.answer("Mo‘ljalni yozing (ixtiyoriy). Yo‘q bo‘lsa 0 deb yuboring:", reply_markup=main_menu())


@router.message(SellerShopStates.landmark, F.text)
async def shop_landmark(message: Message, state: FSMContext, api):
    landmark = "" if message.text.strip() == "0" else message.text.strip()
    data = await state.get_data()

    payload = {
        "name": data["name"],
        "phone": data["phone"],
        "city": data["city"],  # ✅ city_id yuboriladi
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "landmark": landmark,
    }

    try:
        shop = api.create_shop(payload)
    except Exception as e:
        await message.answer(f"❌ API xatolik: {e}", reply_markup=main_menu())
        await state.clear()
        return

    set_seller(message.from_user.id, shop_id=shop["id"], seller_token=shop["seller_token"])

    await message.answer(
        "✅ Do‘kon yaratildi!\n\nEndi kabinetdan foydalaning:",
        reply_markup=shop_menu()
    )
    await state.clear()