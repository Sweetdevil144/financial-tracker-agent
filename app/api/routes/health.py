
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Health"])

@router.get("/health")
def health():
    return {
        "status" : "healthy",
        "date" : datetime.now(timezone.utc)
    }
