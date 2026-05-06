from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserProfileOut(BaseSchema):
    id: str
    full_name: str
    email: str
    phone: str
    telegram_id: int | None = None
    telegram_username: str | None = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
