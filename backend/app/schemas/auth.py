from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.helpers import is_valid_phone, sanitize_text


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class VendorRegisterRequest(BaseSchema):
    business_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    address: str = Field(..., max_length=500)
    description: str | None = Field(None, max_length=1000)
    logo_url: str | None = Field(None, max_length=500)
    vendor_type: Literal["food", "grocery", "pharmacy", "laundry", "fashion", "other"] = "food"
    delivery_fee: Decimal = Field(default=Decimal("0.00"), ge=0)

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
    def validate_phone(cls, value: str) -> str:
        if not is_valid_phone(value):
            raise ValueError("Invalid phone number")
        return value


class UserRegisterRequest(BaseSchema):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_name(cls, value):
        cleaned = sanitize_text(str(value))
        if not cleaned:
            raise ValueError("Invalid name")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not is_valid_phone(value):
            raise ValueError("Invalid phone number")
        return value


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class VerifyEmailRequest(BaseSchema):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    account_type: Literal["user", "vendor"]


class ForgotPasswordRequest(BaseSchema):
    email: EmailStr
    account_type: Literal["user", "vendor"]


class ResetPasswordRequest(BaseSchema):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)
    account_type: Literal["user", "vendor"]


class AuthMessageResponse(BaseSchema):
    message: str
    account_id: str | None = None


class VirtualAccountDetails(BaseSchema):
    account_number: str
    account_name: str
    bank_name: str


class VerifyEmailResponse(AuthMessageResponse):
    virtual_account: VirtualAccountDetails | None = None
