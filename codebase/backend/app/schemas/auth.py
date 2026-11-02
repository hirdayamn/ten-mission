from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: str = "access"