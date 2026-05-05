from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import help as help_handler
from bot.handlers import order as order_handler
from bot.handlers import start as start_handler
from bot.handlers import wallet as wallet_handler
from bot.keyboards.catalogue_keyboard import build_catalogue_keyboard
from bot.keyboards.order_keyboard import build_main_menu
from bot.keyboards.vendor_keyboard import build_vendor_keyboard
from bot.services import api_client
from bot.state import redis_state
from bot.utils import formatters


logger = logging.getLogger("venzap.bot.rule_engine")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await help_handler.send_help(update, context)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data or ""
    if data.startswith("intent:"):
        intent = data.split(":", 1)[1]
        await handle_intent({"intent": intent}, update, context)
        return

    if data.startswith("vendor:"):
        vendor_name = data.split(":", 1)[1]
        await handle_intent({"intent": "select_vendor", "vendor_name": vendor_name}, update, context)
        return

    if data.startswith("item:"):
        item_name = data.split(":", 1)[1]
        await handle_intent(
            {"intent": "select_items", "items": [{"name": item_name, "quantity": 1}]},
            update,
            context,
        )
        return

    await help_handler.send_help(update, context)


async def handle_intent(intent_payload: dict[str, Any], update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    intent = str(intent_payload.get("intent") or "unclear")

    if intent in {"unclear", "out_of_scope"}:
        await help_handler.send_help(update, context)
        return

    if intent == "greet":
        await start_handler.start_command(update, context)
        return

    if intent == "faq":
        await help_handler.send_help(update, context, intent_payload.get("faq_answer"))
        return

    if intent == "list_vendors":
        vendors = await api_client.get_active_vendors()
        if not vendors:
            await message.reply_text("No active vendors are available right now.", reply_markup=build_main_menu())
            return
        text = "Available vendors:\n" + formatters.format_vendor_list(vendors)
        await message.reply_text(text, reply_markup=build_vendor_keyboard(vendors))
        return

    if intent in {"select_vendor", "view_catalogue"}:
        vendor_name = intent_payload.get("vendor_name")
        if not vendor_name:
            vendor_name = await redis_state.get_selected_vendor(user.id)
        if not vendor_name:
            await message.reply_text("Please choose a vendor first.", reply_markup=build_main_menu())
            return
        await redis_state.set_selected_vendor(user.id, vendor_name)
        await _show_catalogue(update, context, vendor_name)
        return

    if intent == "select_items":
        items = intent_payload.get("items") or []
        if not items:
            await message.reply_text("Tell me which items you want.", reply_markup=build_main_menu())
            return
        cart = await redis_state.get_cart(user.id)
        updated = _merge_cart(cart, items)
        await redis_state.set_cart(user.id, updated)
        text = "Added to cart:\n" + formatters.format_cart(updated)
        await message.reply_text(text, reply_markup=build_main_menu())
        return

    if intent == "remove_item":
        items = intent_payload.get("items") or []
        if not items:
            await message.reply_text("Tell me which item to remove.", reply_markup=build_main_menu())
            return
        cart = await redis_state.get_cart(user.id)
        updated = _remove_from_cart(cart, items)
        await redis_state.set_cart(user.id, updated)
        text = "Updated cart:\n" + formatters.format_cart(updated)
        await message.reply_text(text, reply_markup=build_main_menu())
        return

    if intent == "view_cart":
        cart = await redis_state.get_cart(user.id)
        await message.reply_text(formatters.format_cart(cart), reply_markup=build_main_menu())
        return

    if intent == "clear_cart":
        await redis_state.clear_cart(user.id)
        await message.reply_text("Cart cleared.", reply_markup=build_main_menu())
        return

    if intent == "enter_address":
        address = intent_payload.get("address")
        if not address:
            await message.reply_text("Please provide a delivery address.", reply_markup=build_main_menu())
            return
        await redis_state.set_delivery_address(user.id, address)
        await message.reply_text("Delivery address saved.", reply_markup=build_main_menu())
        return

    if intent == "confirm_order":
        cart = await redis_state.get_cart(user.id)
        address = await redis_state.get_delivery_address(user.id)
        if not cart:
            await message.reply_text("Your cart is empty.", reply_markup=build_main_menu())
            return
        if not address:
            await message.reply_text("Please provide a delivery address first.", reply_markup=build_main_menu())
            return
        summary = "Order summary:\n" + formatters.format_cart(cart) + f"\nAddress: {address}"
        await order_handler.show_order_menu(update, context, summary)
        return

    if intent == "cancel_order":
        await redis_state.clear_cart(user.id)
        await redis_state.clear_delivery_address(user.id)
        await message.reply_text("Order cancelled.", reply_markup=build_main_menu())
        return

    if intent in {"check_balance", "fund_wallet", "view_account"}:
        await wallet_handler.show_wallet_menu(update, context)
        return

    if intent == "order_status":
        await order_handler.show_order_menu(update, context, latest_only=True)
        return

    if intent == "order_history":
        await order_handler.show_order_menu(update, context)
        return

    await help_handler.send_help(update, context)


def _merge_cart(cart: list[dict[str, Any]], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {str(item.get("name")): int(item.get("quantity", 1)) for item in cart if item.get("name")}
    for item in items:
        name = item.get("name")
        if not name:
            continue
        qty = int(item.get("quantity", 1))
        merged[name] = merged.get(name, 0) + max(1, qty)
    return [{"name": name, "quantity": qty} for name, qty in merged.items()]


def _remove_from_cart(cart: list[dict[str, Any]], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    remove_names = {str(item.get("name")) for item in items if item.get("name")}
    return [item for item in cart if item.get("name") not in remove_names]


async def _show_catalogue(update: Update, context: ContextTypes.DEFAULT_TYPE, vendor_name: str) -> None:
    message = update.effective_message
    if not message:
        return

    vendors = await api_client.get_active_vendors()
    vendor = next(
        (item for item in vendors if item.get("name") == vendor_name or item.get("business_name") == vendor_name),
        None,
    )
    if not vendor:
        await message.reply_text("Vendor not found.", reply_markup=build_main_menu())
        return

    vendor_id = str(vendor.get("id"))
    items = await api_client.get_vendor_catalogue(vendor_id)
    text = f"Catalogue for {vendor_name}:\n" + formatters.format_catalogue(items)
    await message.reply_text(text, reply_markup=build_catalogue_keyboard(items))
