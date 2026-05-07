from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import get_current_user, get_db, require_internal_secret
from app.models import Order
from app.schemas.orders import OrderCreateRequest, OrderListResponse, OrderOut
from app.services.order_service import create_order, get_orders_by_telegram_id, get_user_orders
from app.utils.limiter import limiter


router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def _order_out(order: Order) -> OrderOut:
	items = [
		{
			"name": item.name,
			"price": item.price,
			"quantity": item.quantity,
		}
		for item in order.items
	]
	vendor_name = order.vendor.business_name if order.vendor else ""
	return OrderOut(
		id=str(order.id),
		status=order.status,
		vendor_id=str(order.vendor_id),
		vendor_name=vendor_name,
		delivery_address=order.delivery_address,
		delivery_fee=order.delivery_fee,
		subtotal=order.subtotal,
		total=order.total,
		note=order.note,
		created_at=order.created_at,
		items=items,
	)


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_orders)
async def place_order(
	request: Request,
	payload: OrderCreateRequest,
	db: AsyncSession = Depends(get_db),
	user=Depends(get_current_user),
) -> OrderOut:
	order = await create_order(db, user, payload)
	stmt = (
		select(Order)
		.options(selectinload(Order.items), selectinload(Order.vendor))
		.where(Order.id == order.id)
	)
	order_full = (await db.execute(stmt)).scalar_one()
	return _order_out(order_full)


@router.get("/history", response_model=OrderListResponse)
async def order_history(
	page: int = Query(1, ge=1),
	page_size: int = Query(20, ge=1, le=100),
	db: AsyncSession = Depends(get_db),
	user=Depends(get_current_user),
) -> OrderListResponse:
	orders, total = await get_user_orders(db, user, page, page_size)
	return OrderListResponse(
		data=[_order_out(order) for order in orders],
		page=page,
		page_size=page_size,
		total=total,
	)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
	order_id: str,
	db: AsyncSession = Depends(get_db),
	user=Depends(get_current_user),
) -> OrderOut:
	stmt = (
		select(Order)
		.options(selectinload(Order.items), selectinload(Order.vendor))
		.where(Order.id == order_id, Order.user_id == user.id)
	)
	order = (await db.execute(stmt)).scalar_one_or_none()
	if not order:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
	return _order_out(order)


@router.get("/bot/history", response_model=OrderListResponse)
async def bot_order_history(
	request: Request,
	telegram_id: int = Query(..., ge=1),
	page: int = Query(1, ge=1),
	page_size: int = Query(5, ge=1, le=50),
	db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
	require_internal_secret(request)
	orders, total = await get_orders_by_telegram_id(db, telegram_id, page, page_size)
	return OrderListResponse(
		data=[_order_out(order) for order in orders],
		page=page,
		page_size=page_size,
		total=total,
	)
