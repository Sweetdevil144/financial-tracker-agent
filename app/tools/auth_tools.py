import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

import jwt

from app.config import config
from app.database.core_data import insert_one, read_one, update_one
from app.models.auth import AuthResponse, Token, User
from app.utils.constants import Collection


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def generate_jwt_token(user_id: str, email: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
    return token, expires_at.isoformat()


async def create_user(email: str, password: str, name: str) -> AuthResponse:
    existing = await read_one(
        collection_name=Collection.USERS,
        data_filter={"email": email, "deleted": False},
    )
    if existing:
        return AuthResponse(success=False, message="Email already registered")

    user_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "_id": user_id,
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
        "created_at": now,
        "deleted": False,
    }

    result = await insert_one(document=user_doc, collection_name=Collection.USERS)
    if not result.acknowledged:
        return AuthResponse(success=False, message="Failed to create user")

    token, expires_at = generate_jwt_token(user_id, email)
    await store_token(user_id=user_id, token=token, expires_at=expires_at)

    return AuthResponse(
        success=True,
        message="User created successfully",
        user_id=user_id,
        token=token,
    )


async def authenticate_user(email: str, password: str) -> AuthResponse:
    user_doc = await read_one(
        collection_name=Collection.USERS,
        data_filter={"email": email, "deleted": False},
    )
    if not user_doc:
        return AuthResponse(success=False, message="Invalid email or password")

    if not verify_password(password, user_doc["password_hash"]):
        return AuthResponse(success=False, message="Invalid email or password")

    user_id = user_doc["_id"]
    token, expires_at = generate_jwt_token(user_id, email)
    await store_token(user_id=user_id, token=token, expires_at=expires_at)

    return AuthResponse(
        success=True,
        message="Login successful",
        user_id=user_id,
        token=token,
    )


async def store_token(user_id: str, token: str, expires_at: str) -> None:
    token_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    token_doc = {
        "_id": token_id,
        "user_id": user_id,
        "token": token,
        "created_at": now,
        "expires_at": expires_at,
        "revoked": False,
    }
    await insert_one(document=token_doc, collection_name=Collection.TOKENS)


async def verify_token_in_db(token: str) -> Optional[Token]:
    token_doc = await read_one(
        collection_name=Collection.TOKENS,
        data_filter={"token": token, "revoked": False},
    )
    if not token_doc:
        return None
    return Token(**token_doc)


async def revoke_token(token: str) -> bool:
    result = await update_one(
        collection_name=Collection.TOKENS,
        filter={"token": token},
        update={"$set": {"revoked": True}},
    )
    return result.modified_count > 0


async def revoke_all_user_tokens(user_id: str) -> int:
    result = await update_one(
        collection_name=Collection.TOKENS,
        filter={"user_id": user_id, "revoked": False},
        update={"$set": {"revoked": True}},
    )
    return result.modified_count
