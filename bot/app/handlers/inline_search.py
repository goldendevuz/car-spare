import asyncio
import hashlib

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from ..services.storage import get_last_city

router = Router()


def _result_id(*parts) -> str:
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()[:32]


@router.inline_query()
async def inline_search(inline_query: InlineQuery, api):
    query = inline_query.query.strip()
    user_id = inline_query.from_user.id

    city_id = get_last_city(user_id)
    if not city_id:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=_result_id("no-city", user_id),
                    title="Avval hududni tanlang",
                    description="Botga o'ting: 🌍 Hudud tugmasini bosing",
                    input_message_content=InputTextMessageContent(
                        message_text="Hududni tanlash uchun botga o'tib 🌍 Hudud tugmasini bosing."
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    if len(query) < 2:
        await inline_query.answer(results=[], cache_time=1, is_personal=True)
        return

    try:
        data = await asyncio.to_thread(
            api.search, city_id=city_id, query=query, telegram_id=user_id, page=1, page_size=10
        )
    except Exception:
        await inline_query.answer(results=[], cache_time=1, is_personal=True)
        return

    results = []
    for r in data.get("results", []):
        text = (
            f"🏪 {r.get('shop_name', '-')}\n"
            f"🧩 {r.get('best_part', '-')}\n"
            f"📍 {r.get('landmark', '-')}\n"
            f"📞 {r.get('phone', '-')}"
        )
        results.append(
            InlineQueryResultArticle(
                id=_result_id(r.get("shop_id"), r.get("best_part_id")),
                title=r.get("shop_name", "-"),
                description=f"{r.get('best_part', '-')} | {r.get('phone', '-')}",
                input_message_content=InputTextMessageContent(message_text=text),
            )
        )

    if not results:
        results = [
            InlineQueryResultArticle(
                id=_result_id("empty", query),
                title="Hech narsa topilmadi",
                description="Boshqa nom bilan urinib ko'ring",
                input_message_content=InputTextMessageContent(message_text=f"🔎 \"{query}\" bo'yicha hech narsa topilmadi."),
            )
        ]

    await inline_query.answer(results=results, cache_time=1, is_personal=True)
