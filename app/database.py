import os
from dataclasses import dataclass, field
from typing import Any


def _split_ints(raw: str) -> list[int]:
    if not raw:
        return []
    result: list[int] = []
    for part in raw.split(","):
        item = part.strip()
        if not item:
            continue
        try:
            result.append(int(item))
        except ValueError:
            continue
    return result


@dataclass
class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_TG_IDS: list[int] = field(default_factory=lambda: _split_ints(os.getenv("ADMIN_TG_IDS", "")))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./novamind.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")
    REMOVE_BG_API_KEY: str = os.getenv("REMOVE_BG_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    FREE_DAILY_CREDIT: int = int(os.getenv("FREE_DAILY_CREDIT", "25"))
    INITIAL_BALANCE: int = int(os.getenv("INITIAL_BALANCE", "100"))
    REFERRAL_BONUS: int = int(os.getenv("REFERRAL_BONUS", "50"))
    REFERRAL_THRESHOLD: int = int(os.getenv("REFERRAL_THRESHOLD", "1"))
    SERVICE_COSTS: dict[str, int] = field(
        default_factory=lambda: {
            "image_generation": 12,
            "image_to_image": 14,
            "background_removal": 8,
            "text_generation": 6,
            "summarize": 5,
            "translate": 5,
            "text_to_speech": 6,
            "speech_to_text": 7,
            "video_generation": 15,
            "image_enhancement": 9,
        }
    )
    DISABLED_SERVICES: set[str] = field(default_factory=set)


settings = Settings()


def is_admin_chat_id(chat_id: int) -> bool:
    return chat_id in settings.ADMIN_TG_IDS
