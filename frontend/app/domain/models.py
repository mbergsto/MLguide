from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict

class MetaData(BaseModel):
    phases: List[str]
    clusters: List[str]
    paradigms: List[str]
    tasks: List[str]
    dataset_type: List[str]
    conditions: List[str]
    performancePrefs: List[str]
    
class Option(BaseModel):
    iri: str
    label: str
    
class RecommendationRequest(BaseModel):
    problem_text: str | None = None
    phase_iri: str | None = None
    cluster_iris: list[str] = Field(default_factory=list)
    paradigm_iri: str | None = None
    max_results: int = Field(default=10, ge=1)
    task_iri: str | None = None
    conditions: list[str] = Field(default_factory=list)
    performance_prefs: list[str] = Field(default_factory=list)
    dataset_type_iri: str | None = None
    
class RecommendationItem(BaseModel):
    method: str | None = None
    methodLabel: str | None = None
    approach: str | None = None
    approachLabel: str | None = None
    supportingArticles: int | None = None
    possibleIfMatches: int | None = None
    performanceMatches: int | None = None
    taskMatch: int | None = None
    
class ArticleItem(BaseModel):
    article: str | None = None
    doi: str
    label: str | None = None


class MatchGroups(BaseModel):
    conditions: list[Option] = Field(default_factory=list)
    performance: list[Option] = Field(default_factory=list)
    tasks: list[Option] = Field(default_factory=list)


class RecommendationDetailsResponse(BaseModel):
    approachIri: str
    articles: list[ArticleItem] = Field(default_factory=list)
    matches: MatchGroups


class RecommendationListResponse(BaseModel):
    results: list[RecommendationItem] = Field(default_factory=list)


class UserSession(BaseModel):
    id: int
    username: str
    created_at: str


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


class SavedSearch(SavedSearchPayload):
    id: int
    user_id: int
    created_at: str
