from fastapi import APIRouter

from app.services.user_context import JWTAuthUser

router = APIRouter(prefix="/expenses")

auth = JWTAuthUser()
