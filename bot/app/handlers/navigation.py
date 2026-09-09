from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.common import main_menu, shop_menu, phone_kb, cancel_inline_kb
from ..keyboards.cities import cities_kb
from ..states import SellerShopStates, SearchStates, FeedbackStates
from ..services.storage import get_seller, delete_seller, set_last_city, get_last_city

router = Router()

MAIN_MENU_TEXT = (
    "<b>ZapchastTOP botiga xush kelibsiz 🚗</b>\n\n"
    "🔎 <b>Qidiruv</b> — <u>zapchast qidiring</u>\n"
    "🏪 <b>Mening do‘konim</b> — sotuvchilar uchun kabinet\n"
    "💬 <b>Fikr bildiring</b> — taklif yoki shikoyat yuboring"
)


@router.callback_query(F.data == "nav:main")
async def nav_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "nav:myshop")
async def nav_my_shop(cb: CallbackQuery, state: FSMContext, api):
    await state.clear()

    info = get_seller(cb.from_user.id)
    if info and not api.shop_exists(info["shop_id"]):
        delete_seller(cb.from_user.id)
        info = None

    if info:
        await cb.message.edit_text("Do‘kon kabineti:", reply_markup=shop_menu())
        await cb.answer()
        return

    # Do'kon yo'q bo'lsa: registratsiya boshlanadi (telefon reply-keyboard talab qiladi)
    await state.set_state(SellerShopStates.phone)
    await cb.message.edit_text("Do‘kon yaratish uchun telefon raqamingizni yuboring 👇")
    await cb.message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_kb())
    await cb.answer()


@router.callback_query(F.data == "nav:search")
async def nav_search(cb: CallbackQuery, state: FSMContext, api):
    await state.clear()

    city_id = get_last_city(cb.from_user.id)
    if city_id:
        await state.update_data(city_id=city_id, page=1, query=None)
        await state.set_state(SearchStates.query)
        await cb.message.edit_text(
            "<b>Zapchast nomini yozing</b> <i>(masalan: Cobalt old fara):</i>",
            reply_markup=cancel_inline_kb("search"),
            parse_mode="HTML",
        )
        await cb.answer()
        return

    try:
        cities = api.list_cities()
    except Exception as e:
        await cb.message.edit_text(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        await cb.answer()
        return

    if not cities:
        await cb.message.edit_text("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        await cb.answer()
        return

    await state.set_state(SearchStates.city)
    await cb.message.edit_text("Qaysi hudud (shahar)da qidiramiz?", reply_markup=cities_kb(cities, prefix="city"))
    await cb.answer()


@router.callback_query(F.data == "nav:feedback")
async def nav_feedback(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FeedbackStates.waiting_text)
    await cb.message.edit_text(
        "Fikringizni yozib yuboring (taklif/shikoyat):",
        reply_markup=cancel_inline_kb("feedback"),
    )
    await cb.answer()


@router.callback_query(F.data == "nav:hudud")
async def nav_city(cb: CallbackQuery, state: FSMContext, api):
    await state.clear()

    try:
        cities = api.list_cities()
    except Exception as e:
        await cb.message.edit_text(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        await cb.answer()
        return

    if not cities:
        await cb.message.edit_text("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        await cb.answer()
        return

    current_city_id = get_last_city(cb.from_user.id)
    await cb.message.edit_text(
        "Hududni tanlang:",
        reply_markup=cities_kb(cities, prefix="setcity", selected_id=current_city_id),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("setcity:"))
async def set_city(cb: CallbackQuery):
    city_id = cb.data.split(":", 1)[1]
    set_last_city(cb.from_user.id, city_id)

    city_name = None
    if cb.message and cb.message.reply_markup:
        for row in cb.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == cb.data:
                    city_name = btn.text.removeprefix("✅ ")

    await cb.message.edit_text(f"✅ Hudud tanlandi: {city_name or city_id}", reply_markup=main_menu())
    await cb.answer()


# ---------- generic cancel ----------
@router.callback_query(F.data.startswith("cancel:"))
async def cancel_flow(cb: CallbackQuery, state: FSMContext):
    target = cb.data.split(":", 1)[1]
    await state.clear()

    if target == "shop":
        info = get_seller(cb.from_user.id)
        if info:
            await cb.message.edit_text("Do‘kon kabineti:", reply_markup=shop_menu())
        else:
            await cb.message.edit_text(MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")
    elif target == "part":
        await cb.message.edit_text("Do‘kon kabineti:", reply_markup=shop_menu())
    else:
        await cb.message.edit_text(MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")

    await cb.answer()
