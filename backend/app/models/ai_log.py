from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AILog(Base):
    __tablename__ = "ai_logs"
    __table_args__ = (
        Index("ix_ai_logs_user_id_created_at_desc", "user_id", text("created_at DESC")),
        Index("ix_ai_logs_parsed_intent", "parsed_intent"),
        Index("ix_ai_logs_fallback_used", "fallback_used"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    sanitized: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    parsed_intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parsed_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    was_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fallback_used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User | None"] = relationship(back_populates="ai_logs")
