from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.config import settings


@dataclass
class GuardrailResult:
    is_valid: bool
    data: dict[str, Any] | None
    failure_reason: str | None = None

    @classmethod
    def fail(cls, reason: str) -> "GuardrailResult":
        return cls(is_valid=False, data=None, failure_reason=reason)

    @classmethod
    def pass_(cls, data: dict[str, Any]) -> "GuardrailResult":
        return cls(is_valid=True, data=data, failure_reason=None)


class GuardrailValidator:
    ALLOWED_INTENTS = {
        "greet",
        "list_vendors",
        "select_vendor",
        "view_catalogue",
        "select_items",
        "remove_item",
        "view_cart",
        "clear_cart",
        "confirm_order",
        "cancel_order",
        "enter_address",
        "check_balance",
        "fund_wallet",
        "view_account",
        "order_status",
        "order_history",
        "faq",
        "unclear",
        "out_of_scope",
    }

    def __init__(self, confidence_threshold: float | None = None) -> None:
        self.confidence_threshold = (
            confidence_threshold if confidence_threshold is not None else settings.ai_confidence_threshold
        )

    def validate(
        self,
        llm_output: str,
        active_vendors: list[dict[str, Any]],
        vendor_catalogue: list[dict[str, Any]] | None,
    ) -> GuardrailResult:
        try:
            data = json.loads(llm_output)
        except Exception:
            return GuardrailResult.fail("JSON_PARSE_ERROR")

        required = {
            "intent": str,
            "vendor_name": (str, type(None)),
            "items": list,
            "address": (str, type(None)),
            "faq_answer": (str, type(None)),
            "clarification": (str, type(None)),
            "confidence": float,
        }
        for field, expected_type in required.items():
            if field not in data:
                return GuardrailResult.fail(f"MISSING_FIELD:{field}")
            if not isinstance(data[field], expected_type):
                return GuardrailResult.fail(f"WRONG_TYPE:{field}")

        if data["intent"] not in self.ALLOWED_INTENTS:
            return GuardrailResult.fail("INVALID_INTENT")

        if data["vendor_name"] is not None:
            valid_names = [vendor.get("name") for vendor in active_vendors]
            if data["vendor_name"] not in valid_names:
                data["vendor_name"] = None
                data["intent"] = "unclear"
                data["clarification"] = "Which vendor would you like?"

        if data.get("items") and vendor_catalogue:
            valid_items = {item.get("name") for item in vendor_catalogue}
            data["items"] = [item for item in data["items"] if item.get("name") in valid_items]
            if not data["items"]:
                data["intent"] = "unclear"
                data["clarification"] = "I couldn't find those items. What would you like?"

        for item in data.get("items", []):
            qty = item.get("quantity", 1)
            if not isinstance(qty, int) or not (1 <= qty <= 20):
                item["quantity"] = 1

        if data.get("confidence", 0.0) < self.confidence_threshold:
            data["intent"] = "unclear"
            data["clarification"] = data.get("clarification") or "Could you rephrase that? I want to get it right!"

        forbidden_patterns = [
            r"system\s*prompt",
            r"ignore\s+instructions",
            r"wallet\s*balance",
            r"₦\d+",
            r"\d{10}",
            r"account\s*number",
            r"password",
            r"api[_\s]?key",
            r"<script",
            r"javascript:",
        ]
        for field in ["faq_answer", "clarification"]:
            val = data.get(field) or ""
            for pattern in forbidden_patterns:
                if re.search(pattern, val, re.IGNORECASE):
                    return GuardrailResult.fail(f"INJECTION_IN:{field}")

        return GuardrailResult.pass_(data)
