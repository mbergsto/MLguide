from __future__ import annotations

from integrations.api import ApiClient, ApiConfig
from domain.models import RecommendationDetailsResponse, RecommendationRequest, RecommendationItem, Option


def fetch_meta_options(cfg: ApiConfig) -> tuple[
    list[Option],
    list[Option],
    list[Option],
    list[Option],
    list[Option],
    list[Option],
    list[Option],
]:
    with ApiClient(cfg) as client:
        return (
            client.meta.phases(),
            client.meta.clusters(),
            client.meta.paradigms(),
            client.meta.tasks(),
            client.meta.dataset_types(),
            client.meta.conditions(),
            client.meta.performance(),
        )


def fetch_recommendations(cfg: ApiConfig, req: RecommendationRequest) -> list[RecommendationItem]:
    with ApiClient(cfg) as client:
        return client.recommendations.recommend(req)


def fetch_method_details(
    cfg: ApiConfig,
    req: RecommendationRequest,
    approach_iri: str,
) -> RecommendationDetailsResponse:
    with ApiClient(cfg) as client:
        return client.recommendations.details(req, approach_iri)
