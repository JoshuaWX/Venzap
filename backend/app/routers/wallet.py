from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models import Transaction, Wallet
from app.schemas.wallet import (
	WalletBalanceResponse,
	WalletFundLinkRequest,
	WalletFundLinkResponse,
	WalletTransactionListResponse,
	WalletTransactionOut,
)
from app.services.payaza_service import PayazaError, create_payment_link
from app.services.wallet_service import get_balance
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/v1/wallet", tags=["wallet"])


def _transaction_out(transaction: Transaction) -> WalletTransactionOut:
	return WalletTransactionOut(
		id=str(transaction.id),
		type=transaction.type,
		amount=transaction.amount,
		reference=transaction.reference,
		payaza_ref=transaction.payaza_ref,
		source=transaction.source,
		status=transaction.status,
		description=transaction.description,
		created_at=transaction.created_at,
	)


@router.get("/balance", response_model=WalletBalanceResponse)
async def wallet_balance(
	user=Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> WalletBalanceResponse:
	balance = await get_balance(db, str(user.id))
	wallet = await db.scalar(select(Wallet).where(Wallet.user_id == user.id))
	if not wallet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
	return WalletBalanceResponse(balance=balance, currency=wallet.currency, updated_at=wallet.updated_at)


@router.get("/transactions", response_model=WalletTransactionListResponse)
async def list_transactions(
	page: int = Query(1, ge=1),
	page_size: int = Query(20, ge=1, le=100),
	user=Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> WalletTransactionListResponse:
	wallet = await db.scalar(select(Wallet).where(Wallet.user_id == user.id))
	if not wallet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

	offset = (page - 1) * page_size
	total = await db.scalar(select(func.count(Transaction.id)).where(Transaction.wallet_id == wallet.id))
	stmt = (
		select(Transaction)
		.where(Transaction.wallet_id == wallet.id)
		.order_by(Transaction.created_at.desc())
		.offset(offset)
		.limit(page_size)
	)
	transactions = (await db.execute(stmt)).scalars().all()
	return WalletTransactionListResponse(
		data=[_transaction_out(txn) for txn in transactions],
		page=page,
		page_size=page_size,
		total=int(total or 0),
	)


@router.post("/fund/link", response_model=WalletFundLinkResponse)
@limiter.limit(settings.rate_limit_wallet_fund_link)
async def fund_link(
	request: Request,
	payload: WalletFundLinkRequest,
	user=Depends(get_current_user),
) -> WalletFundLinkResponse:
	reference = f"paylink_{uuid4().hex}"
	metadata = {"user_id": str(user.id)}
	try:
		payment_link = await create_payment_link(
			amount=payload.amount,
			email=user.email,
			reference=reference,
			metadata=metadata,
			callback_url=payload.callback_url,
			currency=payload.currency,
		)
	except PayazaError as exc:
		raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

	return WalletFundLinkResponse(payment_url=payment_link.payment_url, reference=payment_link.reference)
