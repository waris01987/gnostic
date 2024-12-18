import re

from app.common.enums import UserType

from app.services.permission import PermissionService
from fastapi import Depends, HTTPException, status, Request

# from starlette import status
from jose import jwt, JWTError
from cachetools import TTLCache
from sqlalchemy.orm import Session

# from starlette.requests import Request
from typing import Optional, Dict, List
from starlette.responses import Response
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import RequestResponseEndpoint

from app.api.response import APIResponse
from app.common.context import UserContext
from app.middlewares.base import BaseMiddleware
from app.common.errors import InvalidAuthorizationHeaderError
from app.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_TYPE
from app.common.constants import UNPROTECTED_ROUTE_PATHS, TRAILING_SLASH


class JWTAuthMiddleware(BaseMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        url_path = (
            request.url.path[:-1]
            if request.url.path[-1] == TRAILING_SLASH
            else request.url.path
        )
        if any(re.search(pattern, url_path) for pattern in UNPROTECTED_ROUTE_PATHS):
            return await call_next(request)

        try:
            access_jwt = self._validate_authorization_header(request=request)
            payload = jwt.decode(
                token=access_jwt,
                key=JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )
            payload = (
                payload.get("user")
                if payload.get("user")
                else payload.get("organisation")
            )
            context_token = UserContext.set(payload)
            request.state.jwt_payload = payload

        except Exception as exc:
            return APIResponse.error(
                message="Invalid or expired token.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        response = await call_next(request)
        UserContext.reset(context_token)
        return response

    @staticmethod
    def _validate_authorization_header(request: Request) -> str:
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(
            authorization_header_value=authorization
        )
        if not authorization or scheme != JWT_TYPE:
            raise InvalidAuthorizationHeaderError(
                "Invalid or missing authorization header."
            )
        return token


role_permission_cache = TTLCache(maxsize=1000, ttl=3600)


class JWTBearerSecurity:
    def __init__(self, permission: Optional[str] = None):
        self.required_permission = permission

    def verify_token(self, token: str) -> dict:
        """Decode and verify the JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def check_permission(self, user_permissions: list):
        """Check if the required permission exists for the user's role."""
        if (
            self.required_permission
            and self.required_permission not in user_permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

    async def __call__(
        self, request: Request, service: PermissionService = Depends(PermissionService)
    ):
        """Authenticate and authorize the current user."""
        # Extract and validate Authorization Header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header.",
            )

        scheme, token = self._get_authorization_scheme_param(authorization)
        if scheme != JWT_TYPE:
            raise InvalidAuthorizationHeaderError(
                "Invalid authorization header scheme."
            )

        # Verify the token and extract payload
        payload = self.verify_token(token)
        if payload.get("user"):
            entity_id = payload["user"]["user_id"]
            entity_type = UserType.INDIVIDUAL_USER.value
        elif payload.get("organisation"):
            entity_id = payload["organisation"]["org_id"]
            entity_type = UserType.ORGANISATION.value
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload."
            )

        # Set user context
        context_token = UserContext.set(payload)
        request.state.jwt_payload = payload

        # Fetch the user's permissions
        user_permissions = await service.get_user_permissions(entity_id, entity_type)

        # Check if the required permission is present
        self.check_permission(user_permissions)

        return context_token

    @staticmethod
    def _get_authorization_scheme_param(authorization_header_value: str):
        parts = authorization_header_value.split()
        if len(parts) != 2:
            raise InvalidAuthorizationHeaderError(
                "Invalid authorization header format."
            )
        return parts[0], parts[1]
