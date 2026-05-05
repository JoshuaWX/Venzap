from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.catalogue import CatalogueItemOut
from app.utils.helpers import is_valid_phone, sanitize_text


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class VendorPublicOut(BaseSchema):
    id: str
    business_name: str
    name: str
    vendor_type: str
    description: str | None = None
    logo_url: str | None = None
    delivery_fee: Decimal
    is_open: bool


class VendorListResponse(BaseSchema):
    data: list[VendorPublicOut]
    page: int
    page_size: int
    total: int


class VendorDetailResponse(BaseSchema):
    vendor: VendorPublicOut
    catalogue: list[CatalogueItemOut]


class VendorProfileOut(BaseSchema):
    id: str
    business_name: str
    email: str
    phone: str
    address: str
    description: str | None = None
    logo_url: str | None = None
    vendor_type: str
    delivery_fee: Decimal
    is_active: bool
    is_verified: bool
    is_open: bool


class VendorUpdateRequest(BaseSchema):
    business_name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=1000)
    logo_url: str | None = Field(None, max_length=500)
    vendor_type: str | None = Field(None, max_length=50)
    delivery_fee: Decimal | None = Field(None, ge=0)

    @field_validator("business_name", "address", "description", "logo_url", mode="before")
    @classmethod
    def sanitize_strings(cls, value):
        if value is None:
            return None
        cleaned = sanitize_text(str(value))
        if not cleaned:
            raise ValueError("Invalid value")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not is_valid_phone(value):
            raise ValueError("Invalid phone number")
        return value


class VendorOpenStatusRequest(BaseSchema):
    is_open: bool


class VendorOpenStatusResponse(BaseSchema):
    message: str
    is_open: bool


class VendorDashboardStats(BaseSchema):
    orders_today: int
    revenue_today: Decimal
    total_orders: int
    catalogue_items: int


class VendorEarningsSummary(BaseSchema):
    total_earned: Decimal
    this_month: Decimal
    pending_escrow: Decimal


class VendorPayoutOut(BaseSchema):
    id: str
    order_id: str
    amount: Decimal
    status: str
    released_at: datetime | None = None
    created_at: datetime


class VendorEarningsResponse(BaseSchema):
    summary: VendorEarningsSummary
    history: list[VendorPayoutOut]
