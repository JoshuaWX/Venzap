from __future__ import annotations

from typing import Any


def format_vendor_list(vendors: list[dict[str, Any]]) -> str:
    if not vendors:
        return "No vendors available."
    lines = []
    for index, vendor in enumerate(vendors, start=1):
        name = vendor.get("name") or vendor.get("business_name") or "Vendor"
        vendor_type = vendor.get("vendor_type") or ""
        line = f"{index}. {name}"
        if vendor_type:
            line = f"{line} ({vendor_type})"
        lines.append(line)
    return "\n".join(lines)


def format_catalogue(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No catalogue items available."
    lines = []
    for index, item in enumerate(items, start=1):
        name = item.get("name") or "Item"
        price = item.get("price")
        if price is None:
            lines.append(f"{index}. {name}")
        else:
            lines.append(f"{index}. {name} - {price}")
    return "\n".join(lines)


def format_cart(items: list[dict[str, Any]]) -> str:
    if not items:
        return "Your cart is empty."
    lines = []
    for item in items:
        name = item.get("name") or "Item"
        qty = item.get("quantity", 1)
        lines.append(f"- {name} x{qty}")
    return "\n".join(lines)


def format_order_history(orders: list[dict[str, Any]]) -> str:
    if not orders:
        return "You have no orders yet."
    lines = ["Your recent orders:"]
    for order in orders:
        order_id = order.get("id") or ""
        vendor = order.get("vendor_name") or order.get("vendor") or "Vendor"
        status = order.get("status") or "unknown"
        total = order.get("total")
        total_text = f"{total}" if total is not None else ""
        line = f"- {vendor} | {status} | {total_text} | {order_id}".strip()
        lines.append(line)
    return "\n".join(lines)


def format_order_status(order: dict[str, Any]) -> str:
    order_id = order.get("id") or ""
    vendor = order.get("vendor_name") or order.get("vendor") or "Vendor"
    status = order.get("status") or "unknown"
    total = order.get("total")
    items = order.get("items") or []
    item_text = ", ".join(
        f"{item.get('name', 'Item')} x{item.get('quantity', 1)}" for item in items if isinstance(item, dict)
    )
    total_text = f"{total}" if total is not None else ""
    lines = [
        f"Latest order: {order_id}",
        f"Vendor: {vendor}",
        f"Status: {status}",
    ]
    if item_text:
        lines.append(f"Items: {item_text}")
    if total_text:
        lines.append(f"Total: {total_text}")
    return "\n".join(lines)


def format_account_details(account: dict[str, Any]) -> str:
    bank_name = account.get("bank_name") or "Bank"
    account_number = account.get("account_number") or ""
    account_name = account.get("account_name") or ""
    lines = [
        "Your Venzap wallet account is ready:",
        f"Bank: {bank_name}",
        f"Account: {account_number}",
        f"Name: {account_name}",
    ]
    return "\n".join(lines)
