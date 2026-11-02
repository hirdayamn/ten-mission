from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import create_access_token
from app.core.config import settings
from app.schemas.auth import Token
from app.schemas.members import MemberLogin


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(credentials: MemberLogin):
    access_token = create_access_token({"sub": credentials.email})
    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )