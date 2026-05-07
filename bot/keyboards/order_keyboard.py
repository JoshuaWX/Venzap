from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Browse vendors", callback_data="intent:list_vendors")],
        [InlineKeyboardButton("View cart", callback_data="intent:view_cart")],
        [InlineKeyboardButton("My bank account", callback_data="intent:view_account")],
        [InlineKeyboardButton("Checkout", callback_data="intent:confirm_order")],
        [InlineKeyboardButton("Orders", callback_data="intent:order_history")],
        [InlineKeyboardButton("Help", callback_data="intent:faq")],
    ]
    return InlineKeyboardMarkup(buttons)

