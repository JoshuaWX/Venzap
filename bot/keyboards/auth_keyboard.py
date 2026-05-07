from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_start_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Create account", callback_data="auth:signup")],
        [InlineKeyboardButton("Sign in", callback_data="auth:login")],
        [InlineKeyboardButton("Browse vendors", callback_data="intent:list_vendors")],
        [InlineKeyboardButton("Help", callback_data="intent:faq")],
    ]
    return InlineKeyboardMarkup(buttons)


def build_auth_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Create account", callback_data="auth:signup")],
        [InlineKeyboardButton("Sign in", callback_data="auth:login")],
        [InlineKeyboardButton("Back", callback_data="auth:cancel")],
    ]
    return InlineKeyboardMarkup(buttons)
