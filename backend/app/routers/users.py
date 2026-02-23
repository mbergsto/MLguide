from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import psycopg

from app.services import user_service

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest) -> UserResponse:
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    try:
        row = user_service.login_or_create_user(username)
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="Database error while logging in user") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return UserResponse.model_validate(row)
