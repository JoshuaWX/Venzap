from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_vendor, get_db
from app.models import CatalogueItem, Order, Vendor, VendorPayout
from app.schemas.orders import OrderListResponse, OrderOut, OrderStatusResponse, OrderStatusUpdateRequest
from app.schemas.vendor import (
	VendorDashboardStats,
	VendorEarningsResponse,
	VendorEarningsSummary,
	VendorOpenStatusRequest,
	VendorOpenStatusResponse,
	VendorPayoutOut,
	VendorProfileOut,
	VendorUpdateRequest,
)
from app.services.order_service import get_vendor_orders, update_order_status


router = APIRouter(prefix="/api/v1/vendor", tags=["vendor"])


def _order_out(order: Order) -> OrderOut:
	items = [
		{
			"name": item.name,
			"price": item.price,
			"quantity": item.quantity,
		}
		for item in order.items
	]
	return OrderOut(
		id=str(order.id),
		status=order.status,
		vendor_id=str(order.vendor_id),
		vendor_name=order.vendor.business_name if order.vendor else "",
		delivery_address=order.delivery_address,
		delivery_fee=order.delivery_fee,
		subtotal=order.subtotal,
		total=order.total,
		note=order.note,
		created_at=order.created_at,
		items=items,
	)


@router.get("/profile", response_model=VendorProfileOut)
async def get_profile(
	vendor: Vendor = Depends(get_current_vendor),
) -> VendorProfileOut:
	return VendorProfileOut(
		id=str(vendor.id),
		business_name=vendor.business_name,
		email=vendor.email,
		phone=vendor.phone,
		address=vendor.address,
		description=vendor.description,
		logo_url=vendor.logo_url,
		vendor_type=vendor.vendor_type,
		delivery_fee=vendor.delivery_fee,
		is_active=vendor.is_active,
		is_verified=vendor.is_verified,
		is_open=vendor.is_open,
	)


@router.put("/profile", response_model=VendorProfileOut)
async def update_profile(
	payload: VendorUpdateRequest,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> VendorProfileOut:
	updates = payload.model_dump(exclude_unset=True)
	if "vendor_type" in updates:
		allowed = {"food", "grocery", "pharmacy", "laundry", "fashion", "other"}
		if updates["vendor_type"] not in allowed:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vendor type")

	if "business_name" in updates and updates["business_name"] != vendor.business_name:
		existing = await db.scalar(select(Vendor).where(Vendor.business_name == updates["business_name"]))
		if existing:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Business name already in use")

	if "phone" in updates and updates["phone"] != vendor.phone:
		existing = await db.scalar(select(Vendor).where(Vendor.phone == updates["phone"]))
		if existing:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already in use")

	for key, value in updates.items():
		setattr(vendor, key, value)

	await db.commit()
	await db.refresh(vendor)
	return VendorProfileOut(
		id=str(vendor.id),
		business_name=vendor.business_name,
		email=vendor.email,
		phone=vendor.phone,
		address=vendor.address,
		description=vendor.description,
		logo_url=vendor.logo_url,
		vendor_type=vendor.vendor_type,
		delivery_fee=vendor.delivery_fee,
		is_active=vendor.is_active,
		is_verified=vendor.is_verified,
		is_open=vendor.is_open,
	)


@router.put("/toggle-open", response_model=VendorOpenStatusResponse)
async def toggle_open(
	payload: VendorOpenStatusRequest,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> VendorOpenStatusResponse:
	vendor.is_open = payload.is_open
	await db.commit()
	await db.refresh(vendor)
	message = "Vendor is open" if vendor.is_open else "Vendor is closed"
	return VendorOpenStatusResponse(message=message, is_open=vendor.is_open)


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
	status_filter: str | None = Query(None, alias="status"),
	page: int = Query(1, ge=1),
	page_size: int = Query(20, ge=1, le=100),
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
	orders, total = await get_vendor_orders(db, vendor, status_filter, page, page_size)
	return OrderListResponse(
		data=[_order_out(order) for order in orders],
		page=page,
		page_size=page_size,
		total=total,
	)


@router.put("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def set_order_status(
	order_id: str,
	payload: OrderStatusUpdateRequest,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> OrderStatusResponse:
	allowed = {"pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"}
	if payload.status not in allowed:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status")

	order = await update_order_status(db, vendor, order_id, payload.status)
	return OrderStatusResponse(id=str(order.id), status=order.status)


@router.get("/earnings", response_model=VendorEarningsResponse)
async def get_earnings(
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> VendorEarningsResponse:
	total_stmt = select(func.sum(VendorPayout.amount)).where(
		VendorPayout.vendor_id == vendor.id,
		VendorPayout.status == "released",
	)
	pending_stmt = select(func.sum(VendorPayout.amount)).where(
		VendorPayout.vendor_id == vendor.id,
		VendorPayout.status == "pending",
	)

	start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
	month_stmt = select(func.sum(VendorPayout.amount)).where(
		VendorPayout.vendor_id == vendor.id,
		VendorPayout.status == "released",
		VendorPayout.created_at >= start_of_month,
	)

	total_earned = await db.scalar(total_stmt)
	pending = await db.scalar(pending_stmt)
	this_month = await db.scalar(month_stmt)

	history_stmt = (
		select(VendorPayout)
		.where(VendorPayout.vendor_id == vendor.id)
		.order_by(VendorPayout.created_at.desc())
		.limit(50)
	)
	payouts = (await db.execute(history_stmt)).scalars().all()

	summary = VendorEarningsSummary(
		total_earned=total_earned or 0,
		this_month=this_month or 0,
		pending_escrow=pending or 0,
	)
	history = [
		VendorPayoutOut(
			id=str(payout.id),
			order_id=str(payout.order_id),
			amount=payout.amount,
			status=payout.status,
			released_at=payout.released_at,
			created_at=payout.created_at,
		)
		for payout in payouts
	]
	return VendorEarningsResponse(summary=summary, history=history)


@router.get("/dashboard/stats", response_model=VendorDashboardStats)
async def get_dashboard_stats(
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> VendorDashboardStats:
	start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

	orders_today_stmt = select(func.count(Order.id)).where(
		Order.vendor_id == vendor.id,
		Order.created_at >= start_of_day,
	)
	revenue_today_stmt = select(func.sum(Order.total)).where(
		Order.vendor_id == vendor.id,
		Order.created_at >= start_of_day,
		Order.status != "cancelled",
	)
	total_orders_stmt = select(func.count(Order.id)).where(Order.vendor_id == vendor.id)
	catalogue_count_stmt = select(func.count(CatalogueItem.id)).where(CatalogueItem.vendor_id == vendor.id)

	orders_today = await db.scalar(orders_today_stmt)
	revenue_today = await db.scalar(revenue_today_stmt)
	total_orders = await db.scalar(total_orders_stmt)
	catalogue_items = await db.scalar(catalogue_count_stmt)

	return VendorDashboardStats(
		orders_today=int(orders_today or 0),
		revenue_today=revenue_today or 0,
		total_orders=int(total_orders or 0),
		catalogue_items=int(catalogue_items or 0),
	)
