from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CatalogueItem, Vendor
from app.schemas.catalogue import CatalogueItemOut
from app.schemas.vendor import VendorDetailResponse, VendorListResponse, VendorPublicOut


router = APIRouter(prefix="/api/v1/vendors", tags=["vendors"])


def _vendor_public(vendor: Vendor) -> VendorPublicOut:
	return VendorPublicOut(
		id=str(vendor.id),
		business_name=vendor.business_name,
		name=vendor.business_name,
		vendor_type=vendor.vendor_type,
		description=vendor.description,
		logo_url=vendor.logo_url,
		delivery_fee=vendor.delivery_fee,
		is_open=bool(vendor.is_open),
	)


def _catalogue_item_out(item: CatalogueItem) -> CatalogueItemOut:
	return CatalogueItemOut(
		id=str(item.id),
		vendor_id=str(item.vendor_id),
		name=item.name,
		description=item.description,
		price=item.price,
		emoji=item.emoji,
		category=item.category,
		is_available=bool(item.is_available),
	)


@router.get("/", response_model=VendorListResponse, status_code=status.HTTP_200_OK)
async def list_vendors(
	vendor_type: str | None = Query(None, alias="type"),
	page: int = Query(1, ge=1),
	page_size: int = Query(20, ge=1, le=100),
	db: AsyncSession = Depends(get_db),
) -> VendorListResponse:
	offset = (page - 1) * page_size
	base = select(Vendor).where(Vendor.is_active.is_(True), Vendor.is_open.is_(True))
	if vendor_type:
		base = base.where(Vendor.vendor_type == vendor_type)

	total = await db.scalar(select(func.count()).select_from(base.subquery()))
	stmt = base.order_by(Vendor.business_name.asc()).offset(offset).limit(page_size)
	vendors = (await db.execute(stmt)).scalars().all()

	return VendorListResponse(
		data=[_vendor_public(vendor) for vendor in vendors],
		page=page,
		page_size=page_size,
		total=int(total or 0),
	)


@router.get("/{vendor_id}", response_model=VendorDetailResponse, status_code=status.HTTP_200_OK)
async def get_vendor(
	vendor_id: str,
	db: AsyncSession = Depends(get_db),
) -> VendorDetailResponse:
	vendor = await db.get(Vendor, vendor_id)
	if not vendor or not vendor.is_active:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

	stmt = (
		select(CatalogueItem)
		.where(CatalogueItem.vendor_id == vendor.id, CatalogueItem.is_available.is_(True))
		.order_by(CatalogueItem.name.asc())
	)
	items = (await db.execute(stmt)).scalars().all()

	return VendorDetailResponse(
		vendor=_vendor_public(vendor),
		catalogue=[_catalogue_item_out(item) for item in items],
	)
