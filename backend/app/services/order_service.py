from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CatalogueItem, Order, OrderItem, Transaction, User, Vendor, VendorPayout, Wallet


def _ensure_positive(amount: Decimal) -> None:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")


def _reference(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


async def create_order(session: AsyncSession, user: User, payload) -> Order:
    vendor = await session.get(Vendor, payload.vendor_id)
    if not vendor or not vendor.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    if not vendor.is_open:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vendor is closed")

    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items provided")

    quantities: dict[UUID, int] = {}
    for item in payload.items:
        qty = int(item.quantity)
        if qty <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid quantity")
        quantities[item.catalogue_item_id] = quantities.get(item.catalogue_item_id, 0) + qty

    item_ids = list(quantities.keys())
    stmt = (
        select(CatalogueItem)
        .where(
            CatalogueItem.vendor_id == vendor.id,
            CatalogueItem.id.in_(item_ids),
            CatalogueItem.is_available.is_(True),
        )
    )
    items = (await session.execute(stmt)).scalars().all()
    if len(items) != len(item_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more items are unavailable")

    subtotal = sum((item.price * quantities[item.id] for item in items), Decimal("0.00"))
    delivery_fee = vendor.delivery_fee or Decimal("0.00")
    total = subtotal + delivery_fee
    _ensure_positive(total)

    async with session.begin():
        wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user.id).with_for_update())
        if not wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
        if wallet.balance is None or wallet.balance < total:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        wallet.balance = wallet.balance - total
        transaction = Transaction(
            wallet_id=wallet.id,
            type="escrow",
            amount=total,
            reference=_reference("order"),
            source="order_debit",
            status="success",
            description="Order escrow",
        )
        session.add(transaction)

        order = Order(
            user_id=user.id,
            vendor_id=vendor.id,
            transaction=transaction,
            status="pending",
            delivery_address=payload.delivery_address,
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            total=total,
            note=payload.note,
        )
        session.add(order)

        for item in items:
            qty = quantities[item.id]
            order_item = OrderItem(
                order=order,
                catalogue_item_id=item.id,
                name=item.name,
                price=item.price,
                quantity=qty,
            )
            session.add(order_item)

    await session.refresh(order)
    return order


async def update_order_status(
    session: AsyncSession,
    vendor: Vendor,
    order_id: str,
    status_value: str,
) -> Order:
    order = await session.get(Order, order_id)
    if not order or order.vendor_id != vendor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status == status_value:
        return order

    order.status = status_value

    if status_value == "delivered":
        existing_payout = await session.scalar(select(VendorPayout).where(VendorPayout.order_id == order.id))
        if order.transaction:
            order.transaction.type = "release"
            order.transaction.source = "escrow_release"
            order.transaction.status = "success"
        if not existing_payout:
            payout = VendorPayout(
                vendor_id=vendor.id,
                order_id=order.id,
                amount=order.total,
                status="released",
                released_at=datetime.now(timezone.utc),
            )
            session.add(payout)

    await session.commit()
    await session.refresh(order)
    return order


async def get_user_orders(
    session: AsyncSession,
    user: User,
    page: int,
    page_size: int,
) -> tuple[list[Order], int]:
    offset = (page - 1) * page_size
    total = await session.scalar(select(func.count(Order.id)).where(Order.user_id == user.id))
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.vendor))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = (await session.execute(stmt)).scalars().all()
    return orders, int(total or 0)


async def get_vendor_orders(
    session: AsyncSession,
    vendor: Vendor,
    status_filter: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Order], int]:
    offset = (page - 1) * page_size
    base = select(Order).where(Order.vendor_id == vendor.id)
    if status_filter:
        base = base.where(Order.status == status_filter)

    total = await session.scalar(select(func.count()).select_from(base.subquery()))
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.user), selectinload(Order.vendor))
        .where(Order.vendor_id == vendor.id)
    )
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    stmt = stmt.order_by(Order.created_at.desc()).offset(offset).limit(page_size)

    orders = (await session.execute(stmt)).scalars().all()
    return orders, int(total or 0)


async def get_orders_by_telegram_id(
    session: AsyncSession,
    telegram_id: int,
    page: int,
    page_size: int,
) -> tuple[list[Order], int]:
    offset = (page - 1) * page_size
    total_stmt = (
        select(func.count(Order.id))
        .join(User, User.id == Order.user_id)
        .where(User.telegram_id == telegram_id)
    )
    total = await session.scalar(total_stmt)

    stmt = (
        select(Order)
        .join(User, User.id == Order.user_id)
        .options(selectinload(Order.items), selectinload(Order.vendor))
        .where(User.telegram_id == telegram_id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = (await session.execute(stmt)).scalars().all()
    return orders, int(total or 0)
