from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_vendor, get_db
from app.models import CatalogueItem, Vendor
from app.schemas.catalogue import CatalogueCreateRequest, CatalogueItemOut, CatalogueUpdateRequest


router = APIRouter(prefix="/api/v1/catalogue", tags=["catalogue"])


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


@router.get("/vendor/{vendor_id}", response_model=list[CatalogueItemOut])
async def get_vendor_catalogue(
	vendor_id: str,
	include_unavailable: bool = Query(False),
	db: AsyncSession = Depends(get_db),
) -> list[CatalogueItemOut]:
	vendor = await db.get(Vendor, vendor_id)
	if not vendor or not vendor.is_active:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

	stmt = select(CatalogueItem).where(CatalogueItem.vendor_id == vendor.id)
	if not include_unavailable:
		stmt = stmt.where(CatalogueItem.is_available.is_(True))
	stmt = stmt.order_by(CatalogueItem.name.asc())
	items = (await db.execute(stmt)).scalars().all()
	return [_catalogue_item_out(item) for item in items]


@router.post("/", response_model=CatalogueItemOut, status_code=status.HTTP_201_CREATED)
async def create_catalogue_item(
	payload: CatalogueCreateRequest,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> CatalogueItemOut:
	item = CatalogueItem(
		vendor_id=vendor.id,
		name=payload.name,
		description=payload.description,
		price=payload.price,
		emoji=payload.emoji,
		category=payload.category,
		is_available=payload.is_available,
	)
	db.add(item)
	await db.commit()
	await db.refresh(item)
	return _catalogue_item_out(item)


@router.put("/{item_id}", response_model=CatalogueItemOut)
async def update_catalogue_item(
	item_id: str,
	payload: CatalogueUpdateRequest,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> CatalogueItemOut:
	item = await db.get(CatalogueItem, item_id)
	if not item or item.vendor_id != vendor.id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")

	updates = payload.model_dump(exclude_unset=True)
	for key, value in updates.items():
		setattr(item, key, value)

	await db.commit()
	await db.refresh(item)
	return _catalogue_item_out(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalogue_item(
	item_id: str,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> None:
	item = await db.get(CatalogueItem, item_id)
	if not item or item.vendor_id != vendor.id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")
	await db.delete(item)
	await db.commit()
	return None


@router.put("/{item_id}/toggle", response_model=CatalogueItemOut)
async def toggle_catalogue_item(
	item_id: str,
	vendor: Vendor = Depends(get_current_vendor),
	db: AsyncSession = Depends(get_db),
) -> CatalogueItemOut:
	item = await db.get(CatalogueItem, item_id)
	if not item or item.vendor_id != vendor.id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")

	item.is_available = not bool(item.is_available)
	await db.commit()
	await db.refresh(item)
	return _catalogue_item_out(item)
