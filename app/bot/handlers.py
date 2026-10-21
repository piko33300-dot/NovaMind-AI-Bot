from __future__ import annotations

from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot.keyboards import main_menu_keyboard
from app.config import settings
from app.database import SessionLocal
from app.service_layer import (
    get_or_create_user,
    handle_start_with_referral,
    get_user_stats,
    get_remaining_daily_credit,
    is_admin_chat_id,
    set_daily_credit,
    set_service_cost,
    toggle_service,
    broadcast_message,
)

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


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    await message.answer(
        "لوحة المشرف:\n"
        "/admin_stats\n"
        "/set_daily_credit 25\n"
        "/set_service_cost image_generation 10\n"
        "/toggle_service image_generation off\n"
        "/broadcast رسالة عامة\n"
        "/ban 123456789\n"
        "/unban 123456789\n"
    )


@router.message(Command("admin_stats"))
async def admin_stats(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    async with SessionLocal() as session:
        user = await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name or "User",
        )
        stats = await get_user_stats(session, user)
        await message.answer(
            f"إحصائيات النظام:\n"
            f"الرصيد الحالي: {stats.get('balance', 0)}\n"
            f"الحد اليومي المتبقي: {stats.get('daily_remaining', 0)}\n"
            f"عدد الإحالات: {stats.get('referrals_count', 0)}"
        )


@router.message(Command("set_daily_credit"))
async def set_daily_credit_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    try:
        value = int(message.get_args()[0])
    except (IndexError, ValueError):
        await message.answer("⚠️ استخدم الشكل: /set_daily_credit 25")
        return

    async with SessionLocal() as session:
        await set_daily_credit(session, value)
    await message.answer(f"✅ تم تحديث الحد اليومي إلى {value}.")


@router.message(Command("set_service_cost"))
async def set_service_cost_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    try:
        args = message.get_args()
        service_name = args[0]
        cost = int(args[1])
    except (IndexError, ValueError):
        await message.answer("⚠️ استخدم الشكل: /set_service_cost image_generation 10")
        return

    async with SessionLocal() as session:
        await set_service_cost(session, service_name, cost)
    await message.answer(f"✅ تم تحديث تكلفة الخدمة {service_name} إلى {cost}.")


@router.message(Command("toggle_service"))
async def toggle_service_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    try:
        args = message.get_args()
        service_name = args[0]
        state = args[1].lower()
    except (IndexError, ValueError):
        await message.answer("⚠️ استخدم الشكل: /toggle_service image_generation off")
        return

    enabled = state in {"on", "1", "true", "yes"}
    async with SessionLocal() as session:
        await toggle_service(session, service_name, enabled)
    await message.answer(f"✅ تم تحديث حالة الخدمة {service_name} إلى {'مفعلة' if enabled else 'معطلة'}.")


@router.message(Command("broadcast"))
async def broadcast_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    args = message.get_args()
    if not args:
        await message.answer("⚠️ استخدم الشكل: /broadcast رسالة عامة")
        return

    text = " ".join(args)
    async with SessionLocal() as session:
        await broadcast_message(session, text)
    await message.answer("✅ تم إرسال الرسالة العامة.")


@router.message(Command("ban"))
async def ban_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    try:
        user_id = int(message.get_args()[0])
    except (IndexError, ValueError):
        await message.answer("⚠️ استخدم الشكل: /ban 123456789")
        return

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        target = result.scalar_one_or_none()
        if target is None:
            await message.answer("⚠️ هذا المستخدم غير موجود.")
            return

        target.is_banned = True
        await session.commit()
    await message.answer(f"✅ تم حظر المستخدم {user_id}.")


@router.message(Command("unban"))
async def unban_command(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin_chat_id(message.from_user.id):
        await message.answer("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    try:
        user_id = int(message.get_args()[0])
    except (IndexError, ValueError):
        await message.answer("⚠️ استخدم الشكل: /unban 123456789")
        return

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        target = result.scalar_one_or_none()
        if target is None:
            await message.answer("⚠️ هذا المستخدم غير موجود.")
            return

        target.is_banned = False
        await session.commit()
    await message.answer(f"✅ تم إلغاء حظر المستخدم {user_id}.")


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
        async with SessionLocal() as session:
            user = await get_or_create_user(
                session,
                message.from_user.id if message.from_user else 0,
                message.from_user.username if message.from_user else None,
                message.from_user.full_name if message.from_user else "User",
            )
            remaining = await get_remaining_daily_credit(session, user.id)
            await message.answer(f"رصيدك الحالي: {user.balance} | الرصيد اليومي المتبقي: {remaining}")
        return

    if text == "🎁 الدعوات والمكافآت":
        await message.answer(
            "شارك رابطك مع أصدقائك للحصول على مكافآت الإحالة.\n"
            "كل مستخدم جديد ينضم عبر كودك يحصل على مكافأة، والـ referrer يحصل على المكافأة بعد التفعيل."
        )
        return

    if text == "📖 طريقة الاستخدام":
        await message.answer(
            "1) اختر الخدمة.\n"
            "2) أرسل المطلوب.\n"
            "3) انتظر النتيجة.\n"
            "4) راقب الرصيد اليومي."
        )
        return

    if text == "💬 الدعم الفني":
        await message.answer("للتواصل مع الدعم، أرسل تفاصيل المشكلة وسيتم مراجعتها في أقرب وقت.")
        return

    await message.answer(
        f"الخدمة: {text}\n"
        "المعالجة الفعلية تتطلب مفتاح API صحيح في المتغيرات البيئية. "
        "الآن البوت جاهز للربط مع الخدمة الفعلية."
    )


@router.message()
async def fallback_message(message: Message) -> None:
    await message.answer(
        "مرحبًا بك في NovaMind AI.\n\n"
        "استخدم القائمة أو اكتب /help للاطلاع على الخدمات المتاحة."
    )