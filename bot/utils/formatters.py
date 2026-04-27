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
