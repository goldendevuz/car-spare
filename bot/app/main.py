import asyncio
import logging

from aiogram import Bot, Dispatcher

from .config import settings
from .services.api_client import ApiClient

from .handlers.start import router as start_router
from .handlers.seller_shop import router as shop_router
from .handlers.seller_part import router as part_router
from .handlers.products import router as products_router
from .handlers.search import router as search_router
from .handlers.feedback import router as feedback_router
from .handlers.navigation import router as navigation_router
from .handlers.inline_search import router as inline_search_router

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, text: str) -> None:
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            logger.exception("Failed to notify admin %s", admin_id)


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp["api"] = ApiClient(
        shop_create_url=settings.shop_create_url,
        part_create_url=settings.part_create_url,
        api_base=settings.api_base,
    )
    dp.include_router(navigation_router)
    dp.include_router(start_router)
    dp.include_router(shop_router)
    dp.include_router(part_router)
    dp.include_router(products_router)
    dp.include_router(search_router)
    dp.include_router(feedback_router)
    dp.include_router(inline_search_router)

    async def on_startup(**_):
        await notify_admins(bot, "✅ Bot ishga tushdi.")

    async def on_shutdown(**_):
        await notify_admins(bot, "⛔ Bot to'xtadi.")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())