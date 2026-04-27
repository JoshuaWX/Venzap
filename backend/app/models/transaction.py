from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('credit','debit','escrow','release')",
            name="ck_transactions_type",
        ),
        CheckConstraint(
            "source IN ('virtual_account','payment_link','order_debit','escrow_release')",
            name="ck_transactions_source",
        ),
        CheckConstraint(
            "status IN ('pending','success','failed')",
            name="ck_transactions_status",
        ),
        Index("ix_transactions_wallet_id_created_at_desc", "wallet_id", text("created_at DESC")),
        Index("ix_transactions_reference", "reference"),
        Index("ix_transactions_payaza_ref", "payaza_ref"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    payaza_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'virtual_account'"),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")
    order: Mapped["Order | None"] = relationship(back_populates="transaction", uselist=False)
