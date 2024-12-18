from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette import status

from app.schemas.auth import (
    IndividualRegistration,
    OrganisationRegistration,
    Login,
    AccessJWT,
    RequestResetPassword,
    ResetPassword,
    OAuthCallbackPayload,
    TokenRefreshRequest,
    ChangePassword,
    OTPResetPassword,
)
from app.services.auth import AuthService
from app.api.response import APIResponse

router = APIRouter(tags=["Authentication"])


@router.post(
    "/registration/individual",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Individual User successfully registered."},
        409: {"description": "User with provided email address already exists."},
    },
)
async def individual_registration(
    payload: IndividualRegistration, service: AuthService = Depends(AuthService)
):
    response_data = await service.individual_registration(payload=payload)
    return APIResponse.success(
        message="Individual User successfully registered.", data=response_data
    )


@router.post(
    "/registration/organisation",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Organisation successfully registered."},
        409: {"description": "User with provided email address already exists."},
    },
)
async def company_registration(
    payload: OrganisationRegistration, service: AuthService = Depends(AuthService)
):
    response_data = await service.register_organisation(payload=payload)
    return APIResponse.success(
        message="Organisation successfully registered.", data=response_data
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User successfully logged in."},
        401: {"description": "Invalid credentials."},
    },
)
async def login(
    request: Request, payload: Login, service: AuthService = Depends(AuthService)
) -> AccessJWT:
    auth_data = await service.login(request=request, payload=payload)
    return APIResponse.success(message="Successfully logged in.", data=auth_data)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(payload: ChangePassword, service: AuthService = Depends(AuthService)) -> AccessJWT:
    auth_data = await service.change_password(payload=payload)
    return APIResponse.success(
        message="Password has been changed successfully", data=auth_data
    )


@router.post(
    "/request-password-reset",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Email sent for request reset password"},
        401: {"description": "Invalid credentials."},
    },
)
async def request_password_reset(
    payload: RequestResetPassword, service: AuthService = Depends(AuthService)
):
    await service.request_password_reset(payload.email)
    return APIResponse.success(message="Email sent for request reset password")


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully reset password for provided email"},
        401: {"description": "Invalid credentials."},
    },
)
async def reset_password(
    payload: ResetPassword, service: AuthService = Depends(AuthService)
):
    await service.reset_password(payload.token, payload.new_password)
    return APIResponse.success(message="Successfully reset password")


@router.post(
    "/send-otp-reset-password",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Email sent for otp for reset password"},
        401: {"description": "Invalid credentials."},
    },
)
async def send_password_reset_otp(
    payload: RequestResetPassword, service: AuthService = Depends(AuthService)
):
    await service.send_reset_password_otp_mail(payload.email)
    return APIResponse.success(message="Email sent for request reset password")


@router.post(
    "/verify-otp-reset-password",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully reset password for provided email"},
        401: {"description": "Invalid credentials."},
    },
)
async def verify_otp_reset_password(
    payload: OTPResetPassword, service: AuthService = Depends(AuthService)
):
    await service.verify_otp_reset_password(payload)
    return APIResponse.success(message="Successfully reset password")


@router.get("/profile_details", status_code=status.HTTP_200_OK)
async def verify_otp_reset_password(
    request: Request, service: AuthService = Depends(AuthService)
):
    response_data = await service.get_profile_details(request=request)
    return APIResponse.success(
        message="Successfully got profile details", data=response_data
    )


@router.post("/oauth/callback", status_code=200)
async def oauth_callback(
    request: Request,
    payload: OAuthCallbackPayload,
    service: AuthService = Depends(AuthService),
):
    return await service.oauth_login(request=request, payload=payload)


@router.post(
    "/token/refresh",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Tokens validated and refreshed as needed."},
        401: {"description": "Invalid or expired tokens."},
    },
)
async def refresh_token(
    token_request: TokenRefreshRequest, service: AuthService = Depends(AuthService)
) -> AccessJWT:
    return await service.handle_token_refresh(token_request)
