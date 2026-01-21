from fastapi import APIRouter, Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.models.auth import AuthResponse, LoginRequest, SignupRequest
from app.tools.auth_tools import authenticate_user, create_user, revoke_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, response: Response):
    result = await create_user(
        email=request.email,
        password=request.password,
        name=request.name,
    )
    if not result.success:
        response.status_code = HTTP_400_BAD_REQUEST
        return result

    if result.token:
        response.set_cookie(
            key="access_token",
            value=result.token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )
    return result


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    result = await authenticate_user(email=request.email, password=request.password)
    if not result.success:
        response.status_code = HTTP_401_UNAUTHORIZED
        return result

    if result.token:
        response.set_cookie(
            key="access_token",
            value=result.token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )
    return result


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "Logged out successfully"}
