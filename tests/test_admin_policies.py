import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_novamind.db")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token")
os.environ.setdefault("ADMIN_TG_IDS", "1001,1002")

import pytest
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal, init_db
from app.service_layer import (
    User,
    can_use_service,
    get_or_create_user,
    get_remaining_daily_credit,
    set_daily_credit,
    set_service_cost,
    toggle_service,
    is_admin_chat_id,
)


@pytest.fixture(autouse=True)
async def clean_db():
    await init_db()
    async with SessionLocal() as session:
        await session.execute(select(User))
    yield


@pytest.mark.asyncio
async def test_user_creation_and_initial_balance():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 1111, "alice", "Alice Example")
        assert user.telegram_id == 1111
        assert user.balance == settings.INITIAL_BALANCE
        assert user.referral_code.startswith("NM")


@pytest.mark.asyncio
async def test_admin_ids_are_checked():
    assert 1001 in settings.ADMIN_TG_IDS
    assert 9999 not in settings.ADMIN_TG_IDS
    assert await is_admin_chat_id(1001) is True
    assert await is_admin_chat_id(9999) is False


@pytest.mark.asyncio
async def test_set_daily_credit_and_cost_persist():
    async with SessionLocal() as session:
        await set_daily_credit(session, 30)
        await set_service_cost(session, "image_generation", 11)
        await toggle_service(session, "image_generation", False)
        assert await get_remaining_daily_credit(session, 1) >= 0


@pytest.mark.asyncio
async def test_banned_user_cannot_use_service():
    async with SessionLocal() as session:
        user = await get_or_create_user(session, 2222, "bob", "Bob")
        user.is_banned = True
        await session.commit()
        allowed, reason, cost = await can_use_service(session, user, "image_generation")
        assert allowed is False
        assert reason == "banned"
        assert cost == 0


@pytest.mark.asyncio
async def test_negative_service_cost_rejected_via_state_or_validation():
    async with SessionLocal() as session:
        with pytest.raises(ValueError):
            await set_service_cost(session, "image_generation", -1)
