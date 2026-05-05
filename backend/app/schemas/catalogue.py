from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.helpers import sanitize_text


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CatalogueItemOut(BaseSchema):
    id: str
    vendor_id: str
    name: str
    description: str | None = None
    price: Decimal
    emoji: str | None = None
    category: str | None = None
    is_available: bool


class CatalogueCreateRequest(BaseSchema):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=1000)
    price: Decimal = Field(..., ge=0)
    emoji: str | None = Field(None, max_length=10)
    category: str | None = Field(None, max_length=100)
    is_available: bool = True

    @field_validator("name", "description", "emoji", "category", mode="before")
    @classmethod
    def sanitize_strings(cls, value):
        if value is None:
            return None
        cleaned = sanitize_text(str(value))
        if not cleaned:
            raise ValueError("Invalid value")
        return cleaned


class CatalogueUpdateRequest(BaseSchema):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    price: Decimal | None = Field(None, ge=0)
    emoji: str | None = Field(None, max_length=10)
    category: str | None = Field(None, max_length=100)
    is_available: bool | None = None

    @field_validator("name", "description", "emoji", "category", mode="before")
    @classmethod
    def sanitize_optional(cls, value):
        if value is None:
            return None
        cleaned = sanitize_text(str(value))
        if not cleaned:
            raise ValueError("Invalid value")
        return cleaned
