from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.helpers import sanitize_text


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CartItem(BaseSchema):
    name: str = Field(..., max_length=255)
    quantity: int = Field(default=1, ge=1, le=20)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, value: Any) -> str:
        cleaned = sanitize_text(str(value))
        return cleaned


class AiParseRequest(BaseSchema):
    message: str = Field(..., max_length=2000)
    telegram_id: int | None = None
    current_step: str | None = Field(None, max_length=64)
    selected_vendor_name: str | None = Field(None, max_length=255)
    cart_items: list[CartItem] | None = None

    @field_validator("message", mode="before")
    @classmethod
    def sanitize_message(cls, value: Any) -> str:
        return sanitize_text(str(value))

    @field_validator("current_step", "selected_vendor_name", mode="before")
    @classmethod
    def sanitize_optional(cls, value: Any) -> str | None:
        if value is None:
            return None
        cleaned = sanitize_text(str(value))
        return cleaned or None


class AiParseResponse(BaseSchema):
    is_valid: bool
    data: dict[str, Any] | None = None
    failure_reason: str | None = None
    raw_output: str | None = None
