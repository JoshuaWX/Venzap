"""initial schema

Revision ID: 20260427_0001
Revises:
Create Date: 2026-04-27 00:01:00

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260427_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_username", sa.String(length=100), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("telegram_id"),
    )

    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("vendor_type", sa.String(length=50), server_default=sa.text("'food'"), nullable=False),
        sa.Column("delivery_fee", sa.Numeric(precision=10, scale=2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_open", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "vendor_type IN ('food','grocery','pharmacy','laundry','fashion','other')",
            name="ck_vendors_vendor_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_name"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(
        "ix_vendors_vendor_type_is_active_is_open",
        "vendors",
        ["vendor_type", "is_active", "is_open"],
        unique=False,
    )

    op.create_table(
        "ai_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("raw_input", sa.Text(), nullable=False),
        sa.Column("sanitized", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("parsed_intent", sa.String(length=50), nullable=True),
        sa.Column("parsed_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("was_valid", sa.Boolean(), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_logs_fallback_used", "ai_logs", ["fallback_used"], unique=False)
    op.create_index("ix_ai_logs_parsed_intent", "ai_logs", ["parsed_intent"], unique=False)
    op.create_index(
        "ix_ai_logs_user_id_created_at_desc",
        "ai_logs",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "catalogue_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("emoji", sa.String(length=10), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_catalogue_items_vendor_id_category",
        "catalogue_items",
        ["vendor_id", "category"],
        unique=False,
    )
    op.create_index(
        "ix_catalogue_items_vendor_id_is_available",
        "catalogue_items",
        ["vendor_id", "is_available"],
        unique=False,
    )

    op.create_table(
        "virtual_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_number", sa.String(length=20), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("bank_name", sa.String(length=100), nullable=False),
        sa.Column("bank_code", sa.String(length=10), nullable=True),
        sa.Column("payaza_ref", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_number"),
        sa.UniqueConstraint("payaza_ref"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_virtual_accounts_account_number", "virtual_accounts", ["account_number"], unique=False)
    op.create_index("ix_virtual_accounts_user_id", "virtual_accounts", ["user_id"], unique=False)

    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("balance", sa.Numeric(precision=12, scale=2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default=sa.text("'NGN'"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("balance >= 0", name="ck_wallets_balance_non_negative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_wallets_user_id", "wallets", ["user_id"], unique=False)

    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("payaza_ref", sa.String(length=255), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("processed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payaza_ref"),
    )
    op.create_index("ix_webhook_events_payaza_ref", "webhook_events", ["payaza_ref"], unique=False)
    op.create_index(
        "ix_webhook_events_processed_created_at_desc",
        "webhook_events",
        ["processed", sa.text("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=False),
        sa.Column("payaza_ref", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=30), server_default=sa.text("'virtual_account'"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('pending','success','failed')", name="ck_transactions_status"),
        sa.CheckConstraint(
            "source IN ('virtual_account','payment_link','order_debit','escrow_release')",
            name="ck_transactions_source",
        ),
        sa.CheckConstraint("type IN ('credit','debit','escrow','release')", name="ck_transactions_type"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    op.create_index("ix_transactions_payaza_ref", "transactions", ["payaza_ref"], unique=False)
    op.create_index("ix_transactions_reference", "transactions", ["reference"], unique=False)
    op.create_index(
        "ix_transactions_wallet_id_created_at_desc",
        "transactions",
        ["wallet_id", sa.text("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("delivery_address", sa.Text(), nullable=False),
        sa.Column("delivery_fee", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','confirmed','preparing','out_for_delivery','delivered','cancelled')",
            name="ck_orders_status",
        ),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_transaction_id", "orders", ["transaction_id"], unique=False)
    op.create_index(
        "ix_orders_user_id_created_at_desc",
        "orders",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_orders_vendor_id_status_created_at_desc",
        "orders",
        ["vendor_id", "status", sa.text("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("catalogue_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint("quantity >= 1", name="ck_order_items_quantity_min_1"),
        sa.ForeignKeyConstraint(["catalogue_item_id"], ["catalogue_items.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_catalogue_item_id", "order_items", ["catalogue_item_id"], unique=False)
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)

    op.create_table(
        "vendor_payouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('pending','released','failed')", name="ck_vendor_payouts_status"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vendor_payouts_order_id", "vendor_payouts", ["order_id"], unique=False)
    op.create_index("ix_vendor_payouts_vendor_id", "vendor_payouts", ["vendor_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vendor_payouts_vendor_id", table_name="vendor_payouts")
    op.drop_index("ix_vendor_payouts_order_id", table_name="vendor_payouts")
    op.drop_table("vendor_payouts")

    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_index("ix_order_items_catalogue_item_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_vendor_id_status_created_at_desc", table_name="orders")
    op.drop_index("ix_orders_user_id_created_at_desc", table_name="orders")
    op.drop_index("ix_orders_transaction_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_transactions_wallet_id_created_at_desc", table_name="transactions")
    op.drop_index("ix_transactions_reference", table_name="transactions")
    op.drop_index("ix_transactions_payaza_ref", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_webhook_events_processed_created_at_desc", table_name="webhook_events")
    op.drop_index("ix_webhook_events_payaza_ref", table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index("ix_wallets_user_id", table_name="wallets")
    op.drop_table("wallets")

    op.drop_index("ix_virtual_accounts_user_id", table_name="virtual_accounts")
    op.drop_index("ix_virtual_accounts_account_number", table_name="virtual_accounts")
    op.drop_table("virtual_accounts")

    op.drop_index("ix_catalogue_items_vendor_id_is_available", table_name="catalogue_items")
    op.drop_index("ix_catalogue_items_vendor_id_category", table_name="catalogue_items")
    op.drop_table("catalogue_items")

    op.drop_index("ix_ai_logs_user_id_created_at_desc", table_name="ai_logs")
    op.drop_index("ix_ai_logs_parsed_intent", table_name="ai_logs")
    op.drop_index("ix_ai_logs_fallback_used", table_name="ai_logs")
    op.drop_table("ai_logs")

    op.drop_index("ix_vendors_vendor_type_is_active_is_open", table_name="vendors")
    op.drop_table("vendors")

    op.drop_table("users")
