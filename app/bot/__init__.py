"""Backward-compatible exports for bot service helpers."""
from __future__ import annotations

from app.service_layer import (
    award_referral_bonus,
    can_use_service,
    consume_service_points,
    create_referral,
    current_daily_usage,
    get_or_create_system_setting,
    get_or_create_user,
    get_remaining_daily_credit,
    get_service_cost,
    get_system_value,
    get_user_stats,
    handle_start_with_referral,
    record_service_use,
    set_system_setting,
)

__all__ = [
    "get_or_create_system_setting",
    "set_system_setting",
    "get_system_value",
    "get_or_create_user",
    "current_daily_usage",
    "get_remaining_daily_credit",
    "get_service_cost",
    "can_use_service",
    "record_service_use",
    "consume_service_points",
    "get_user_stats",
    "create_referral",
    "award_referral_bonus",
    "handle_start_with_referral",
]
