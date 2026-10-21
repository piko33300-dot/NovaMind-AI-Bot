from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import router
from app.config import settings, validate_settings
from app.database import init_db


_SERVICE_API_KEYS = {
    "image_generation": ("OPENAI_API_KEY", "STABILITY_API_KEY"),
    "image_to_image": ("OPENAI_API_KEY", "STABILITY_API_KEY"),
    "background_removal": ("REMOVE_BG_API_KEY",),
    "text_generation": ("OPENAI_API_KEY",),
    "summarize": ("OPENAI_API_KEY",),
    "translate": ("OPENAI_API_KEY",),
    "text_to_speech": ("ELEVENLABS_API_KEY",),
    "speech_to_text": ("OPENAI_API_KEY",),
    "video_generation": ("STABILITY_API_KEY",),
    "image_enhancement": ("STABILITY_API_KEY",),
}


def service_status(service_name: str) -> tuple[bool, str]:
    key_names = _SERVICE_API_KEYS.get(service_name, ())
    if not key_names:
        return False, f"{service_name} غير مهيأة: لا يوجد تعريف خدمة."
    for key_name in key_names:
        env_value = getattr(settings, key_name, "")
        if env_value:
            return True, f"الخدمة {service_name} جاهزة."
    return False, (
        f"غير مهيأة: أضف {', '.join(key_names)} إلى متغيرات البيئة أو استخدم مفتاح API صالح."
    )


async def main() -> None:
    validate_settings()
    await init_db()

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
