from __future__ import annotations

from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot.keyboards import main_menu_keyboard
from app.config import settings
from app.database import SessionLocal
from app.service_layer import get_or_create_user, handle_start_with_referral

router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    if message.from_user is None:
        return

    async with SessionLocal() as session:
        user = await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name or "User",
        )
        referral_code = None
        if message.text:
            parts = message.text.split()
            if len(parts) > 1:
                referral_code = parts[1]
        await handle_start_with_referral(session, user, referral_code)
    await message.answer(
        "مرحبًا بك في NovaMind AI ✨\n\n"
        "أنا بوت عربي يساعدك على استخدام خدمات الذكاء الاصطناعي في مكان واحد.\n"
        "استخدم القائمة أدناه أو اكتب /help لعرض التعليمات.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.answer(
        "قائمة الخدمات المتاحة:\n"
        "• 🎨 توليد الصور\n"
        "• 🪄 إزالة الخلفية\n"
        "• 🎬 إنشاء الفيديو\n"
        "• ✍️ الكتابة والذكاء الاصطناعي\n"
        "• 🔊 تحويل النص إلى صوت\n"
        "• 🌐 الترجمة\n"
        "• 🪙 رصيدي\n"
        "• 🎁 الدعوات والمكافآت\n"
        "• 📖 طريقة الاستخدام\n"
        "• 💬 الدعم الفني\n\n"
        "يمكنك استخدام الأزرار من القائمة أو كتابة اسم الخدمة مباشرة."
    )


@router.message(F.text.in_({
    "🎨 توليد الصور",
    "🪄 إزالة الخلفية",
    "🎬 إنشاء الفيديو",
    "✍️ الكتابة والذكاء الاصطناعي",
    "🔊 تحويل النص إلى صوت",
    "🌐 الترجمة",
    "🪙 رصيدي",
    "🎁 الدعوات والمكافآت",
    "📖 طريقة الاستخدام",
    "💬 الدعم الفني",
}))
async def service_route(message: Message) -> None:
    text = message.text or ""
    if text == "🪙 رصيدي":
        await message.answer("رصيدك الحالي يتم حسابه تلقائيًا عند كل استخدام. اكتب /help للحصول على التعليمات.")
        return
    if text == "🎁 الدعوات والمكافآت":
        await message.answer("شارك رابطك مع أصدقائك للحصول على مكافآت الإحالة. سيتم احتسابها عند التسجيل الجديد.")
        return
    if text == "📖 طريقة الاستخدام":
        await message.answer("1) اختر الخدمة.\n2) أرسل المطلوب.\n3) انتظر النتيجة.\n4) راقب الرصيد اليومي.")
        return
    if text == "💬 الدعم الفني":
        await message.answer("للتواصل مع الدعم، أرسل تفاصيل المشكلة وسيتم مراجعتها في أقرب وقت.")
        return
    await message.answer(f"الخدمة: {text}\nالمعالجة الفعلية تتطلب مفتاح API صحيح في المتغيرات البيئية. الآن البوت جاهز ��لربط مع الخدمة الفعلية.")


@router.message()
async def fallback_message(message: Message) -> None:
    await message.answer(
        "مرحبًا بك في NovaMind AI.\n\n"
        "استخدم القائمة أو اكتب /help للاطلاع على الخدمات المتاحة."
    )
