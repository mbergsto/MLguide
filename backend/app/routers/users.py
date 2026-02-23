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


class SavedSearchPayload(BaseModel):
    problem_text: str | None = None
    phase_iri: str | None = None
    cluster_iris: list[str] | None = None
    paradigm_iri: str | None = None
    max_results: int | None = None
    task_iri: str | None = None
    conditions: list[str] | None = None
    performance_prefs: list[str] | None = None
    dataset_type_iri: str | None = None


class SavedSearchResponse(SavedSearchPayload):
    id: int
    user_id: int
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


@router.get("/{user_id}/saved-searches", response_model=list[SavedSearchResponse])
def list_saved_searches(user_id: int, limit: int = 20) -> list[SavedSearchResponse]:
    try:
        rows = user_service.list_saved_searches(user_id=user_id, limit=limit)
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="Database error while listing saved searches") from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [SavedSearchResponse.model_validate(row) for row in rows]


@router.post("/{user_id}/saved-searches", response_model=SavedSearchResponse)
def create_saved_search(user_id: int, payload: SavedSearchPayload) -> SavedSearchResponse:
    try:
        row = user_service.save_search(user_id=user_id, payload=payload.model_dump())
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="Database error while saving search") from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SavedSearchResponse.model_validate(row)
