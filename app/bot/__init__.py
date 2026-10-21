from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import DailyUsage, Referral, ServiceUsageLog, SystemSetting, User


async def get_or_create_system_setting(session: AsyncSession, key: str, default: str) -> str:
    result = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = SystemSetting(key=key, value=str(default))
        session.add(setting)
        await session.commit()
        return str(default)
    return setting.value


async def set_system_setting(session: AsyncSession, key: str, value: str) -> str:
    result = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = SystemSetting(key=key, value=str(value))
        session.add(setting)
    else:
        setting.value = str(value)
    await session.commit()
    return str(value)


async def get_system_value(session: AsyncSession, key: str, default: str) -> str:
    result = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting is None:
        return str(default)
    return setting.value


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: Optional[str], full_name: str) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is not None:
        if username and not user.username:
            user.username = username
        if full_name and not user.full_name:
            user.full_name = full_name
        await session.commit()
        return user

    code = f"NM{telegram_id % 10000:04d}"
    probe = await session.execute(select(User).where(User.referral_code == code))
    while probe.scalar_one_or_none() is not None:
        code = f"NM{telegram_id % 10000:04d}{len(code)}"
        probe = await session.execute(select(User).where(User.referral_code == code))

    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name or "Unnamed user",
        balance=settings.INITIAL_BALANCE,
        referral_code=code,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def current_daily_usage(session: AsyncSession, user_id: int) -> int:
    today = date.today()
    result = await session.execute(select(DailyUsage).where(DailyUsage.user_id == user_id, DailyUsage.usage_date == today))
    daily = result.scalar_one_or_none()
    return 0 if daily is None else daily.points_used


async def get_remaining_daily_credit(session: AsyncSession, user_id: int) -> int:
    daily_limit = int(await get_system_value(session, "daily_free_credit", str(settings.FREE_DAILY_CREDIT)))
    used = await current_daily_usage(session, user_id)
    return max(0, daily_limit - used)


async def get_service_cost(service_name: str) -> int:
    return int(settings.SERVICE_COSTS.get(service_name, 0))


async def can_use_service(session: AsyncSession, user: User, service_name: str) -> tuple[bool, str, int]:
    cost = await get_service_cost(service_name)
    if cost <= 0:
        return True, "gratis", 0

    daily_remaining = await get_remaining_daily_credit(session, user.id)
    if daily_remaining > 0:
        if daily_remaining >= cost:
            return True, "daily_credit", cost
        if user.balance >= cost - daily_remaining:
            return True, "mixed", cost
        return False, "insufficient_balance", cost

    if user.balance >= cost:
        return True, "balance", cost
    return False, "insufficient_balance", cost


async def record_service_use(
    session: AsyncSession,
    user: User,
    service_name: str,
    status: str,
    points_used: int,
    error_message: Optional[str] = None,
) -> None:
    session.add(
        ServiceUsageLog(
            user_id=user.id,
            service_name=service_name,
            points_used=points_used,
            status=status,
            error_message=error_message,
        )
    )

    today = date.today()
    result = await session.execute(select(DailyUsage).where(DailyUsage.user_id == user.id, DailyUsage.usage_date == today))
    daily = result.scalar_one_or_none()
    if daily is None:
        daily = DailyUsage(user_id=user.id, usage_date=today, points_used=0)
        session.add(daily)

    if status == "success":
        daily.points_used += points_used

    await session.commit()


async def consume_service_points(session: AsyncSession, user: User, service_name: str) -> tuple[bool, str]:
    allowed, reason, cost = await can_use_service(session, user, service_name)
    if not allowed:
        return False, f"الرصيد غير كافٍ. يلزم {cost} نقطة."

    daily_remaining = await get_remaining_daily_credit(session, user.id)
    if daily_remaining > 0:
        used_from_daily = min(daily_remaining, cost)
        used_from_balance = max(0, cost - used_from_daily)
        user.balance -= used_from_balance
        await record_service_use(session, user, service_name, "success", used_from_daily)
        await session.commit()
        return True, "daily_credit" if used_from_balance == 0 else "mixed"

    user.balance -= cost
    await record_service_use(session, user, service_name, "success", cost)
    await session.commit()
    return True, "balance"


async def get_user_stats(session: AsyncSession, user: User) -> dict:
    referrals_count = (await session.execute(select(Referral).where(Referral.referrer_id == user.id))).scalars().all()
    return {
        "referrals_count": len(referrals_count),
        "balance": user.balance,
        "daily_remaining": await get_remaining_daily_credit(session, user.id),
    }


async def create_referral(session: AsyncSession, referrer: User, invitee: User) -> bool:
    if referrer.id == invitee.id:
        return False
    existing = await session.execute(select(Referral).where(Referral.invitee_id == invitee.id))
    if existing.scalar_one_or_none() is not None:
        return False
    invitee.referred_by = referrer.id

    session.add(
        Referral(
            referrer_id=referrer.id,
            invitee_id=invitee.id,
            reward_points=int(await get_system_value(session, "referral_bonus", str(settings.REFERRAL_BONUS))),
            reward_awarded=False,
        )
    )
    await session.commit()
    return True


async def award_referral_bonus(session: AsyncSession, referrer: User, invitee: User) -> bool:
    result = await session.execute(select(Referral).where(Referral.referrer_id == referrer.id, Referral.invitee_id == invitee.id))
    referral = result.scalar_one_or_none()
    if referral is None or referral.reward_awarded:
        return False
    bonus = int(await get_system_value(session, "referral_bonus", str(settings.REFERRAL_BONUS)))
    referrer.balance += bonus
    referral.reward_awarded = True
    await session.commit()
    return True


async def handle_start_with_referral(session: AsyncSession, user: User, code: Optional[str]) -> None:
    if not code:
        return
    result = await session.execute(select(User).where(User.referral_code == code))
    referrer = result.scalar_one_or_none()
    if not referrer or referrer.id == user.id or user.referred_by is not None:
        return
    if await create_referral(session, referrer, user):
        threshold = int(await get_system_value(session, "referral_threshold", str(settings.REFERRAL_THRESHOLD)))
        if threshold <= 1:
            await award_referral_bonus(session, referrer, user)
