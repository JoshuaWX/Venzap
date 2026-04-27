from fastapi import APIRouter, HTTPException, Request, status

from app.config import settings
from app.schemas.ai import AiParseRequest, AiParseResponse
from app.services.ai_service import parse_intent
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


def _require_internal_secret(request: Request) -> None:
	if not settings.internal_ai_secret:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="AI secret not configured",
		)
	secret = request.headers.get("X-Internal-Secret", "")
	if secret != settings.internal_ai_secret:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("/parse", response_model=AiParseResponse)
@limiter.limit(settings.rate_limit_ai_parse)
async def parse_ai(request: Request, payload: AiParseRequest) -> AiParseResponse:
	_require_internal_secret(request)
	cart_items = [item.model_dump() for item in payload.cart_items] if payload.cart_items else None
	result = await parse_intent(
		message=payload.message,
		telegram_id=payload.telegram_id,
		current_step=payload.current_step,
		selected_vendor_name=payload.selected_vendor_name,
		cart_items=cart_items,
	)
	return AiParseResponse(
		is_valid=result.is_valid,
		data=result.data,
		failure_reason=result.failure_reason,
		raw_output=result.raw_output,
	)
