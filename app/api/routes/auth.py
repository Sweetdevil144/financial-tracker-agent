from fastapi import APIRouter, Depends, Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.config import config
from app.models.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.user_context import JWTAuthUser
from app.tools.auth_tools import authenticate_user, create_user, get_user_by_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth = JWTAuthUser()


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

    is_local = config.ENVIRONMENT == "local"
    if result.token:
        response.set_cookie(
            key="access_token",
            value=result.token,
            httponly=True,
            secure=not is_local,
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

    is_local = config.ENVIRONMENT == "local"
    if result.token:
        response.set_cookie(
            key="access_token",
            value=result.token,
            httponly=True,
            secure=not is_local,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )
    return result


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(user_id: str = Depends(auth)):
    user = await get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}
    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
    }
