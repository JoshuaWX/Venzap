from fastapi import APIRouter, Request

from app.services.payaza_service import verify_hmac_sha512
from app.services.webhook_service import parse_json_body, queue_payaza_webhook


router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/payaza")
async def payaza_webhook(request: Request):
	raw_body = await request.body()
	signature = request.headers.get("X-Payaza-Signature", "")

	if not verify_hmac_sha512(raw_body, signature):
		return {"status": "ok"}

	payload = parse_json_body(raw_body)
	if not payload:
		return {"status": "ok"}

	payaza_ref = str(payload.get("reference") or payload.get("id") or "").strip()
	if not payaza_ref:
		return {"status": "ok"}

	queue_payaza_webhook(payload, payaza_ref)
	return {"status": "ok"}
