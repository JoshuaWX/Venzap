from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class WalletBalanceResponse(BaseSchema):
    balance: Decimal
    currency: str
    updated_at: datetime


class WalletTransactionOut(BaseSchema):
    id: str
    type: str
    amount: Decimal
    reference: str
    payaza_ref: str | None = None
    source: str
    status: str
    description: str | None = None
    created_at: datetime


class WalletTransactionListResponse(BaseSchema):
    data: list[WalletTransactionOut]
    page: int
    page_size: int
    total: int


class WalletFundLinkRequest(BaseSchema):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="NGN", min_length=3, max_length=3)
    callback_url: str | None = Field(None, max_length=500)
    success_url: str | None = Field(None, max_length=500)


class WalletFundLinkResponse(BaseSchema):
    payment_url: str
    reference: str
