"""Telegram keyboard definitions for NovaMind AI bot."""
from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🎨 توليد الصور")],
        [KeyboardButton(text="🪄 إزالة الخلفية")],
        [KeyboardButton(text="🎬 إنشاء الفيديو")],
        [KeyboardButton(text="✍️ الكتابة والذكاء الاصطناعي")],
        [KeyboardButton(text="🔊 تحويل النص إلى صوت")],
        [KeyboardButton(text="🌐 الترجمة")],
        [KeyboardButton(text="🪙 رصيدي")],
        [KeyboardButton(text="🎁 الدعوات والمكافآت")],
        [KeyboardButton(text="📖 طريقة الاستخدام")],
        [KeyboardButton(text="💬 الدعم الفني")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)