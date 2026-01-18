from typing import Any

import jwt
from fastapi import HTTPException, status
from starlette.requests import Request

from app.config import config
from app.static import localization
from app.utils.log import logger


def verify_jwt_token(token: str) -> dict[str, Any]:
    decoded_token = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    reserved_claims = ["iss", "sub", "aud", "exp", "nbf", "iat", "jti"]
    for key in reserved_claims:
        if key in decoded_token:
            del decoded_token[key]
    return decoded_token


def get_current_user(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        logger.warning(f"Auth: No access_token cookie found for {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=localization.EXCEPTION_TOKEN_INVALID,
        )
    try:
        if config.ENVIRONMENT == "local":
            return "test_user"
        token_data = verify_jwt_token(token=token)
        logger.info(
            f"Auth: Token verified - user_id={token_data.get('user_id')}, user_type={token_data.get('user_type')}"
        )
        return token_data["user_id"]
    except Exception as e:
        logger.error(f"Auth: Token verification failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=localization.EXCEPTION_TOKEN_INVALID,
        ) from e


class JWTAuthUser:
    def __init__(self) -> None:
        self.token_type = "bearer"
    
    async def __call__(self, request: Request) -> str:
        return get_current_user(request)

    async def _validate_token(self, request: Request) -> str:
        logger.debug(f"Auth: Validating token for {request.method} {request.url.path}")
        current_user = get_current_user(request)
        return current_user
