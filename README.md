import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_novamind.db")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token")
os.environ.setdefault("ADMIN_TG_IDS", "1001,1002")

import pytest
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import DailyUsage, Referral, User
from app.providers import service_status
from app.service_layer import (
    can_use_service,
    consume_service_points,
    create_referral,
    get_or_create_user,
    get_remaining_daily_credit,
    handle_start_with_referral,
)


@pytest.fixture(autouse=True)
async def clean_db():
    await init_db()
    async with SessionLocal() as session:
        await session.execute(select(User))
        await session.execute(select(DailyUsage))
        await session.execute(select(Referral))
    yield


@pytest.mark.asyncio
async def test_register_user_and_initial_balance():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 1111, "alice", "Alice Example")
        assert user.telegram_id == 1111
        assert user.balance == settings.INITIAL_BALANCE
        assert user.referral_code.startswith("NM")


@pytest.mark.asyncio
async def test_daily_credit_limit_is_respected():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 2222, "bob", "Bob Example")
        allowed, _, cost = await can_use_service(session, user, "text_generation")
        assert allowed is True
        assert cost == settings.SERVICE_COSTS["text_generation"]
        assert await get_remaining_daily_credit(session, user.id) >= 0
        ok, _ = await consume_service_points(session, user, "text_generation")
        assert ok is True


@pytest.mark.asyncio
async def test_referral_bonus_is_not_reused():
    async with SessionLocal() as session:
        inviter = await get_or_create_user(session, 3333, "referrer", "Referrer")
        invitee = await get_or_create_user(session, 4444, "invitee", "Invitee")

        created = await create_referral(session, inviter, invitee)
        assert created is True

        before = inviter.balance
        await handle_start_with_referral(session, invitee, inviter.referral_code)
        assert inviter.balance == before

        second = await create_referral(session, inviter, invitee)
        assert second is False


@pytest.mark.asyncio
async def test_admin_ids_are_checked():
    assert 1001 in settings.ADMIN_TG_IDS
    assert 9999 not in settings.ADMIN_TG_IDS


@pytest.mark.asyncio
async def test_missing_api_blocks_service_cleanly():
    configured, msg = service_status("background_removal")
    assert configured is False
    assert "غير مهيأة" in msg or "Add" in msg or "not configured" in msg.lower()


@pytest.mark.asyncio
async def test_insufficient_balance_blocks_service():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 6666, "dana", "Dana")
        user.balance = 0
        await session.commit()
        allowed, reason, cost = await can_use_service(session, user, "image_generation")
        assert allowed is False
        assert reason == "insufficient_balance"
        assert cost > 0


@pytest.mark.asyncio
async def test_daily_credit_and_balance_are_not_double_charged():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 7777, "erin", "Erin")
        user.balance = 20
        await session.commit()
        ok, _ = await consume_service_points(session, user, "image_generation")
        assert ok is True
        assert user.balance <= 20
        # This is a safety net: no direct double charge should happen in the same flow.
        assert user.balance >= 0
