from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.common import products_kb, product_detail_kb, shop_menu
from ..services.storage import get_seller
from ..states import PartEditStates

router = Router()
PAGE_SIZE = 5  # har sahifada nechta tovar


# ---------- helpers ----------
def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


async def render_products_page(
    target: Message | CallbackQuery,
    api,
    shop_id: int,
    seller_token: str,
    page: int,
):
    """
    target: Message yoki CallbackQuery (qaysi joydan chaqirilsa)
    """
    try:
        parts = api.list_parts_seller(shop_id, seller_token)  # ✅ seller endpoint (token bilan)
    except Exception as e:
        text = f"❌ API xatolik (tovarlar): {e}"
        if isinstance(target, CallbackQuery):
            await target.message.answer(text, reply_markup=shop_menu())
            await target.answer()
        else:
            await target.answer(text, reply_markup=shop_menu())
        return

    total = len(parts)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total else 1
    page = max(0, min(page, total_pages - 1))

    start = page * PAGE_SIZE
    items = parts[start:start + PAGE_SIZE]

    text = "📦 *Tovarlarim*\n"
    text += f"Jami: *{total}* ta\n\n"
    if not items:
        text += "Hozircha tovar yo‘q."

    kb = products_kb(page=page, total_pages=total_pages, items=items)

    if isinstance(target, CallbackQuery):
        # xabarni edit qilamiz
        await target.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb, parse_mode="Markdown")


# ---------- entry: "Tovarlarim" button ----------
@router.message(F.text == "📦 Tovarlarim")
async def my_products(message: Message, state: FSMContext, api):
    info = get_seller(message.from_user.id)
    if not info:
        await message.answer("Avval 🏪 Mening do‘konim orqali do‘kon yarating.", reply_markup=shop_menu())
        return

    # sahifani 0 ga qo'yamiz
    await state.update_data(prod_page=0)
    await render_products_page(
        target=message,
        api=api,
        shop_id=info["shop_id"],
        seller_token=info["seller_token"],
        page=0
    )


# ---------- pagination callbacks ----------
@router.callback_query(F.data.startswith("prod:page:"))
async def paginate(cb: CallbackQuery, state: FSMContext, api):
    info = get_seller(cb.from_user.id)
    if not info:
        await cb.answer("Do‘kon topilmadi", show_alert=True)
        return

    page = _safe_int(cb.data.split(":")[-1], 0)
    await state.update_data(prod_page=page)

    await render_products_page(
        target=cb,
        api=api,
        shop_id=info["shop_id"],
        seller_token=info["seller_token"],
        page=page
    )


@router.callback_query(F.data == "prod:noop")
async def noop(cb: CallbackQuery):
    await cb.answer()


@router.callback_query(F.data == "prod:back")
async def back_to_list(cb: CallbackQuery, state: FSMContext, api):
    info = get_seller(cb.from_user.id)
    if not info:
        await cb.answer("Do‘kon topilmadi", show_alert=True)
        return

    data = await state.get_data()
    page = _safe_int(data.get("prod_page", 0), 0)

    await render_products_page(
        target=cb,
        api=api,
        shop_id=info["shop_id"],
        seller_token=info["seller_token"],
        page=page
    )


# ---------- open item ----------
@router.callback_query(F.data.startswith("prod:item:"))
async def open_item(cb: CallbackQuery, state: FSMContext, api):
    info = get_seller(cb.from_user.id)
    if not info:
        await cb.answer("Token topilmadi", show_alert=True)
        return

    part_id = _safe_int(cb.data.split(":")[-1])
    if not part_id:
        await cb.answer("Noto‘g‘ri ID", show_alert=True)
        return

    try:
        part = api.get_part(part_id)
    except Exception as e:
        await cb.answer(f"Xato: {e}", show_alert=True)
        return

    # detail text
    text = (
        f"🧾 *Tovar ma'lumoti*\n\n"
        f"🚗 Model: *{part.get('car_model', '-') }*\n"
        f"🔧 Nomi: *{part.get('name', '-') }*\n"
        f"✅ Mavjudligi: *{'Bor' if part.get('in_stock') else 'Yo‘q'}*\n"
        f"💰 Narx: *{part.get('price') if part.get('price') is not None else 'Ko‘rsatilmagan'}*\n"
        f"🆔 ID: `{part.get('id')}`"
    )

    await cb.message.edit_text(text, reply_markup=product_detail_kb(part_id), parse_mode="Markdown")
    await cb.answer()


# ---------- edit flow ----------
@router.callback_query(F.data.startswith("prod:edit:"))
async def edit_item(cb: CallbackQuery, state: FSMContext):
    part_id = _safe_int(cb.data.split(":")[-1])
    if not part_id:
        await cb.answer("Noto‘g‘ri ID", show_alert=True)
        return

    await state.update_data(edit_part_id=part_id)
    await state.set_state(PartEditStates.waiting_new_name)

    await cb.message.answer("✏️ Yangi nomini yuboring (masalan: Old fara):")
    await cb.answer()


@router.message(PartEditStates.waiting_new_name, F.text)
async def save_edit(message: Message, state: FSMContext, api):
    info = get_seller(message.from_user.id)
    if not info:
        await message.answer("Token topilmadi. /start qiling.", reply_markup=shop_menu())
        await state.clear()
        return

    data = await state.get_data()
    part_id = data.get("edit_part_id")
    new_name = message.text.strip()

    if not part_id or not new_name:
        await message.answer("Noto‘g‘ri ma'lumot. Qayta urinib ko‘ring.", reply_markup=shop_menu())
        await state.clear()
        return

    try:
        api.patch_part(part_id, {"name": new_name}, seller_token=info["seller_token"])
    except Exception as e:
        await message.answer(f"❌ Tahrirlashda xato: {e}", reply_markup=shop_menu())
        await state.clear()
        return

    await message.answer("✅ Saqlandi!", reply_markup=shop_menu())
    await state.clear()


# ---------- delete ----------
@router.callback_query(F.data.startswith("prod:del:"))
async def delete_item(cb: CallbackQuery, state: FSMContext, api):
    info = get_seller(cb.from_user.id)
    if not info:
        await cb.answer("Token topilmadi", show_alert=True)
        return

    part_id = _safe_int(cb.data.split(":")[-1])
    if not part_id:
        await cb.answer("Noto‘g‘ri ID", show_alert=True)
        return

    try:
        api.delete_part(part_id, seller_token=info["seller_token"])
    except Exception as e:
        await cb.answer(f"Xato: {e}", show_alert=True)
        return

    await cb.answer("O‘chirildi ✅")

    # o'chirgandan keyin ro'yxatga qaytamiz
    data = await state.get_data()
    page = _safe_int(data.get("prod_page", 0), 0)

    await render_products_page(
        target=cb,
        api=api,
        shop_id=info["shop_id"],
        seller_token=info["seller_token"],
        page=page
    )