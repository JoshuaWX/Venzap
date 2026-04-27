from __future__ import annotations

from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _trim_callback(value: str, prefix: str, max_len: int = 64) -> str:
    available = max_len - len(prefix)
    safe = value[: max(0, available)]
    return f"{prefix}{safe}"


def build_vendor_keyboard(vendors: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for vendor in vendors[:10]:
        name = vendor.get("name") or vendor.get("business_name") or "Vendor"
        callback = _trim_callback(name, "vendor:")
        buttons.append([InlineKeyboardButton(name, callback_data=callback)])

    buttons.append([InlineKeyboardButton("Main menu", callback_data="intent:faq")])
    return InlineKeyboardMarkup(buttons)
