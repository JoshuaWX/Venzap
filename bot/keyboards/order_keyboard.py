from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Browse vendors", callback_data="intent:list_vendors")],
        [InlineKeyboardButton("View cart", callback_data="intent:view_cart")],
        [InlineKeyboardButton("Wallet", callback_data="intent:check_balance")],
        [InlineKeyboardButton("Orders", callback_data="intent:order_history")],
        [InlineKeyboardButton("Help", callback_data="intent:faq")],
    ]
    return InlineKeyboardMarkup(buttons)
