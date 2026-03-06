from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..states import SearchStates
from ..keyboards.cities import cities_kb
from ..keyboards.search import map_kb, search_page_kb
from ..keyboards.common import main_menu
from ..services.storage import set_last_city, get_last_city

router = Router()

PAGE_SIZE = 3


def format_shop_item(idx: int, r: dict) -> str:
    # r: backenddan kelgan dict
    return (
        f"<b>{idx}️⃣ {r.get('shop_name', '-')}</b>\n"
        f"📍 <i>{r.get('landmark', '-')}</i>\n"
        f"🧩 Topildi: <code>{r.get('best_part', '-')}</code>\n"
        f"📞 <b>{r.get('phone', '-')}</b>"
    )


@router.message(F.text == "🔎 Qidiruv")
async def search_start(message: Message, state: FSMContext, api):
    # Cities ro'yxati
    try:
        cities = api.list_cities()
    except Exception as e:
        await message.answer(f"❌ Shaharlar ro‘yxatini olishda xato: {e}", reply_markup=main_menu())
        return

    if not cities:
        await message.answer("❌ Shaharlar yo‘q. Admin paneldan City qo‘shing.", reply_markup=main_menu())
        return

    await state.set_state(SearchStates.city)
    await message.answer("<b>Qaysi hudud (shahar)da qidiramiz?</b>", reply_markup=cities_kb(cities), parse_mode="HTML")


@router.callback_query(SearchStates.city, F.data.startswith("city:"))
async def search_city_selected(cb: CallbackQuery, state: FSMContext):
    city_id = int(cb.data.split(":")[1])
    await state.update_data(city_id=city_id, page=1, query=None)
    set_last_city(cb.from_user.id, city_id)

    await state.set_state(SearchStates.query)
    await cb.message.answer("<b>Zapchast nomini yozing</b> <i>(masalan: Cobalt old fara):</i>", reply_markup=main_menu(), parse_mode="HTML")
    await cb.answer()


@router.message(SearchStates.query, F.text)
async def search_query(message: Message, state: FSMContext, api):
    query = message.text.strip()
    data = await state.get_data()
    city_id = data.get("city_id")

    if not city_id:
        # fallback: storage'dan olamiz
        city_id = get_last_city(message.from_user.id)
        if not city_id:
            await message.answer("Avval hudud tanlang: 🔎 Qidiruv ni qayta bosing.", reply_markup=main_menu())
            await state.clear()
            return

    await state.update_data(query=query, page=1)

    await _render_search_page(
        message=message,
        api=api,
        telegram_id=message.from_user.id,
        city_id=city_id,
        query=query,
        page=1,
    )


async def _render_search_page(message: Message, api, telegram_id: int, city_id: int, query: str, page: int):
    try:
        res = api.search(city_id=city_id, query=query, telegram_id=telegram_id, page=page, page_size=PAGE_SIZE)
    except Exception as e:
        await message.answer(f"❌ Qidiruvda xato: {e}", reply_markup=main_menu())
        return

    count = res.get("count", 0)
    results = res.get("results", [])
    page_size = res.get("page_size", PAGE_SIZE)
    total_pages = (count + page_size - 1) // page_size if count else 1

    if not results:
        await message.answer("Hech narsa topilmadi 😕\nBoshqa nom bilan urinib ko‘ring.", reply_markup=main_menu())
        return

    await message.answer(f"<b>Topildi!:</b> {count} ta do‘konda\n<b>Sahifa:</b> {page}/{total_pages}", parse_mode='HTML')

    # har do'konni alohida message qilib yuboramiz (map tugmasi uchun qulay)
    base_index = (page - 1) * page_size
    for i, r in enumerate(results, start=1):
        idx = base_index + i
        text = format_shop_item(idx, r)
        await message.answer(text, reply_markup=map_kb(r["shop_id"]), parse_mode="HTML")

    # pagination tugmalari
    await message.answer("Sahifalar:", reply_markup=search_page_kb(page, total_pages))


@router.callback_query(F.data.startswith("s:page:"))
async def search_paginate(cb: CallbackQuery, state: FSMContext, api):
    page = int(cb.data.split(":")[2])
    data = await state.get_data()
    city_id = data.get("city_id")
    query = data.get("query")

    if not city_id or not query:
        await cb.answer("Qidiruv ma'lumoti topilmadi. Qayta 🔎 Qidiruv qiling.", show_alert=True)
        return

    await state.update_data(page=page)
    await cb.message.answer(f"--- Sahifa {page} ---")
    await _render_search_page(
        message=cb.message,
        api=api,
        telegram_id=cb.from_user.id,
        city_id=city_id,
        query=query,
        page=page,
    )
    await cb.answer()


@router.callback_query(F.data == "s:noop")
async def s_noop(cb: CallbackQuery):
    await cb.answer()


@router.callback_query(F.data.startswith("map:"))
async def show_map(cb: CallbackQuery, api):
    shop_id = int(cb.data.split(":")[1])
    try:
        shop = api.get_shop(shop_id)
    except Exception as e:
        await cb.answer(f"Xatolik: {e}", show_alert=True)
        return

    lat = shop.get("latitude")
    lon = shop.get("longitude")
    if lat is None or lon is None:
        await cb.answer("Lokatsiya topilmadi", show_alert=True)
        return

    await cb.message.answer_location(latitude=lat, longitude=lon)
    await cb.answer()