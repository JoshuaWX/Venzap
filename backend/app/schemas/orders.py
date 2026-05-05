from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.helpers import sanitize_text


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OrderItemCreate(BaseSchema):
    catalogue_item_id: UUID
    quantity: int = Field(default=1, ge=1, le=20)


class OrderCreateRequest(BaseSchema):
    vendor_id: UUID
    delivery_address: str = Field(..., max_length=500)
    note: str | None = Field(None, max_length=1000)
    items: list[OrderItemCreate]

    @field_validator("delivery_address", "note", mode="before")
    @classmethod
    def sanitize_strings(cls, value):
        if value is None:
            return None
        cleaned = sanitize_text(str(value))
        if not cleaned:
            raise ValueError("Invalid value")
        return cleaned


class OrderItemOut(BaseSchema):
    name: str
    price: Decimal
    quantity: int


class OrderOut(BaseSchema):
    id: str
    status: str
    vendor_id: str
    vendor_name: str
    delivery_address: str
    delivery_fee: Decimal
    subtotal: Decimal
    total: Decimal
    note: str | None = None
    created_at: datetime
    items: list[OrderItemOut]


class OrderListResponse(BaseSchema):
    data: list[OrderOut]
    page: int
    page_size: int
    total: int


class OrderStatusUpdateRequest(BaseSchema):
    status: str = Field(..., max_length=30)


class OrderStatusResponse(BaseSchema):
    id: str
    status: str
