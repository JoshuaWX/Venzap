from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db
from app.schemas.auth import (
	AuthMessageResponse,
	ForgotPasswordRequest,
	LoginRequest,
	ResetPasswordRequest,
	UserRegisterRequest,
	VendorRegisterRequest,
	VerifyEmailRequest,
	VerifyEmailResponse,
	VirtualAccountDetails,
)
from app.services import auth_service
from app.services.virtual_account_service import ProvisioningError, provision_virtual_account, queue_virtual_account_provisioning
from app.utils.constants import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME
from app.utils.limiter import limiter


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
	response.set_cookie(
		ACCESS_COOKIE_NAME,
		access_token,
		httponly=True,
		secure=settings.cookie_secure,
		samesite="lax",
		max_age=settings.access_token_expire_minutes * 60,
		path="/",
	)
	response.set_cookie(
		REFRESH_COOKIE_NAME,
		refresh_token,
		httponly=True,
		secure=settings.cookie_secure,
		samesite="lax",
		max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
		path="/",
	)


@router.post("/vendor/register", response_model=AuthMessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
async def register_vendor(
	request: Request,
	payload: VendorRegisterRequest,
	db: AsyncSession = Depends(get_db),
) -> AuthMessageResponse:
	vendor = await auth_service.register_vendor(db, payload)
	await auth_service.send_otp(vendor.email, "email_verification_vendor")
	return AuthMessageResponse(message="Vendor account created. Verify your email.", account_id=str(vendor.id))


@router.post("/user/register", response_model=AuthMessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
async def register_user(
	request: Request,
	payload: UserRegisterRequest,
	db: AsyncSession = Depends(get_db),
) -> AuthMessageResponse:
	user = await auth_service.register_user(db, payload)
	await auth_service.send_otp(user.email, "email_verification_user")
	return AuthMessageResponse(message="User account created. Verify your email.", account_id=str(user.id))


@router.post("/vendor/login", response_model=AuthMessageResponse)
@limiter.limit(settings.rate_limit_auth)
async def login_vendor(
	request: Request,
	response: Response,
	payload: LoginRequest,
	db: AsyncSession = Depends(get_db),
) -> AuthMessageResponse:
	vendor = await auth_service.authenticate_vendor(db, payload.email, payload.password)
	tokens = await auth_service.issue_token_pair(subject=str(vendor.id), role="vendor")
	_set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
	return AuthMessageResponse(message="Login successful", account_id=str(vendor.id))


@router.post("/user/login", response_model=AuthMessageResponse)
@limiter.limit(settings.rate_limit_auth)
async def login_user(
	request: Request,
	response: Response,
	payload: LoginRequest,
	db: AsyncSession = Depends(get_db),
) -> AuthMessageResponse:
	user = await auth_service.authenticate_user(db, payload.email, payload.password)
	tokens = await auth_service.issue_token_pair(subject=str(user.id), role="user")
	_set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
	return AuthMessageResponse(message="Login successful", account_id=str(user.id))


@router.post("/refresh", response_model=AuthMessageResponse)
@limiter.limit(settings.rate_limit_auth)
async def refresh_tokens(request: Request, response: Response) -> AuthMessageResponse:
	refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
	if not refresh_token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

	tokens = await auth_service.rotate_refresh_token(refresh_token)
	_set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
	return AuthMessageResponse(message="Token refreshed")


@router.post("/verify-email", response_model=VerifyEmailResponse)
@limiter.limit(settings.rate_limit_auth)
async def verify_email(
	request: Request,
	payload: VerifyEmailRequest,
	db: AsyncSession = Depends(get_db),
) -> VerifyEmailResponse:
	purpose = f"email_verification_{payload.account_type}"
	valid = await auth_service.verify_otp(payload.email, purpose, payload.otp)
	if not valid:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

	if payload.account_type == "vendor":
		vendor = await auth_service.get_vendor_by_email(db, payload.email)
		if not vendor:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
		await auth_service.mark_vendor_verified(db, vendor)
		return VerifyEmailResponse(message="Email verified")

	user = await auth_service.get_user_by_email(db, payload.email)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	await auth_service.mark_user_verified(db, user)

	try:
		virtual_account = await provision_virtual_account(user)
		account_details = VirtualAccountDetails(
			account_number=virtual_account.account_number,
			account_name=virtual_account.account_name,
			bank_name=virtual_account.bank_name,
		)
		return VerifyEmailResponse(message="Email verified", virtual_account=account_details)
	except ProvisioningError:
		queue_virtual_account_provisioning(str(user.id))
		return VerifyEmailResponse(message="Email verified. Wallet account provisioning in progress.")


@router.post("/forgot-password", response_model=AuthMessageResponse)
@limiter.limit(settings.rate_limit_auth)
async def forgot_password(
	request: Request,
	payload: ForgotPasswordRequest,
) -> AuthMessageResponse:
	purpose = f"password_reset_{payload.account_type}"
	await auth_service.send_otp(payload.email, purpose)
	return AuthMessageResponse(message="OTP sent")


@router.post("/reset-password", response_model=AuthMessageResponse)
@limiter.limit(settings.rate_limit_auth)
async def reset_password(
	request: Request,
	payload: ResetPasswordRequest,
	db: AsyncSession = Depends(get_db),
) -> AuthMessageResponse:
	purpose = f"password_reset_{payload.account_type}"
	valid = await auth_service.verify_otp(payload.email, purpose, payload.otp)
	if not valid:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

	if payload.account_type == "vendor":
		vendor = await auth_service.get_vendor_by_email(db, payload.email)
		if not vendor:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
		await auth_service.update_vendor_password(db, vendor, payload.new_password)
	else:
		user = await auth_service.get_user_by_email(db, payload.email)
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
		await auth_service.update_user_password(db, user, payload.new_password)

	return AuthMessageResponse(message="Password updated")
