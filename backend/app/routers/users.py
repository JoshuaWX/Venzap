from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models import Order, VirtualAccount
from app.schemas.auth import VirtualAccountDetails
from app.schemas.orders import OrderListResponse, OrderOut
from app.schemas.user import UserProfileOut
from app.services.order_service import get_user_orders

router = APIRouter(prefix="/api/v1/user", tags=["user"])


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


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(user=Depends(get_current_user)) -> UserProfileOut:
	return UserProfileOut(
		id=str(user.id),
		full_name=user.full_name,
		email=user.email,
		phone=user.phone,
		telegram_id=user.telegram_id,
		telegram_username=user.telegram_username,
		is_verified=user.is_verified,
		is_active=user.is_active,
		created_at=user.created_at,
		updated_at=user.updated_at,
	)


@router.get("/bank-account", response_model=VirtualAccountDetails)
async def get_bank_account(
	user=Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> VirtualAccountDetails:
	account = await db.scalar(select(VirtualAccount).where(VirtualAccount.user_id == user.id))
	if not account:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual account not found")
	return VirtualAccountDetails(
		account_number=account.account_number,
		account_name=account.account_name,
		bank_name=account.bank_name,
	)


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
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


@router.get("/orders/{order_id}", response_model=OrderOut)
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
