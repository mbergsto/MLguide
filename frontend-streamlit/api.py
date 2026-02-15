from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from models import (
    Option,
    RecommendationDetailsResponse,
    RecommendationRequest,
    RecommendationItem,
)

T = TypeVar("T")


@dataclass(frozen=True)
class ApiConfig:
    # Holds API base config
    base_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT", "30"))


class ApiError(Exception):
    # Custom error carrying status + body
    def __init__(self, message: str, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def _parse_json_safe(res: httpx.Response) -> Any:
    # Safely parse JSON or fallback to raw text
    text = res.text
    if not text:
        return None
    try:
        return res.json()
    except Exception:
        return text


class ApiClient:
    # Main HTTP client wrapper
    def __init__(self, config: ApiConfig | None = None):
        # Initialize httpx client with config
        self.config = config or ApiConfig()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        # Close underlying HTTP client
        self._client.close()

    def __enter__(self) -> "ApiClient":
        # Context manager enter
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Context manager exit
        self.close()

    def _get(self, path: str) -> Any:
        # Perform GET request with error handling
        try:
            res = self._client.get(path)
        except Exception as e:
            raise ApiError(f"GET {path} failed (network error)") from e

        body = _parse_json_safe(res)
        if res.is_error:
            raise ApiError(f"GET {path} failed", res.status_code, body)
        return body

    def _post(self, path: str, payload: Any) -> Any:
        # Perform POST request with JSON payload
        try:
            res = self._client.post(
                path,
                json=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
        except Exception as e:
            raise ApiError(f"POST {path} failed (network error)") from e

        body = _parse_json_safe(res)
        if res.is_error:
            raise ApiError(f"POST {path} failed", res.status_code, body)
        return body

    def _parse_model(self, model: type[T], data: Any) -> T:
        # Parse JSON into a Pydantic model
        if isinstance(model, type) and issubclass(model, BaseModel):
            return model.model_validate(data)  # type: ignore[return-value]
        return data  # type: ignore[return-value]

    def _parse_list(self, item_model: type[T], data: Any) -> list[T]:
        # Parse JSON array into typed list
        if not isinstance(data, list):
            raise ApiError("Expected a JSON array", body=data)
        if isinstance(item_model, type) and issubclass(item_model, BaseModel):
            return [item_model.model_validate(x) for x in data]  # type: ignore[misc]
        return data  # type: ignore[return-value]

    class Meta:
        # Wrapper for /meta endpoints
        def __init__(self, outer: "ApiClient"):
            self._ = outer

        def phases(self) -> list[Option]:
            # Fetch lifecycle phases
            return self._._parse_list(Option, self._._get("/meta/phases"))

        def clusters(self) -> list[Option]:
            # Fetch clusters
            return self._._parse_list(Option, self._._get("/meta/clusters"))

        def paradigms(self) -> list[Option]:
            # Fetch learning paradigms
            return self._._parse_list(Option, self._._get("/meta/paradigms"))

        def tasks(self) -> list[Option]:
            # Fetch tasks
            return self._._parse_list(Option, self._._get("/meta/tasks"))

        def dataset_types(self) -> list[Option]:
            # Fetch dataset enums
            return self._._parse_list(Option, self._._get("/meta/enums/dataset-types"))

        def conditions(self) -> list[Option]:
            # Fetch condition enums
            return self._._parse_list(Option, self._._get("/meta/enums/conditions"))

        def performance(self) -> list[Option]:
            # Fetch performance enums
            return self._._parse_list(Option, self._._get("/meta/enums/performance"))

    class Recommendations:
        # Wrapper for recommendation endpoints
        def __init__(self, outer: "ApiClient"):
            self._ = outer

        def recommend(self, req: RecommendationRequest) -> list[RecommendationItem]:
            # Submit recommendation request
            data = self._._post("/recommendations", req.model_dump(exclude_none=True))
            return self._._parse_list(RecommendationItem, data)

        def details(
            self, req: RecommendationRequest, approach_iri: str
        ) -> RecommendationDetailsResponse:
            # Fetch recommendation details
            payload = req.model_dump(exclude_none=True) | {"approach_iri": approach_iri}
            data = self._._post("/recommendations/details", payload)
            return RecommendationDetailsResponse.model_validate(data)

    @property
    def meta(self) -> "ApiClient.Meta":
        # Access meta API
        return ApiClient.Meta(self)

    @property
    def recommendations(self) -> "ApiClient.Recommendations":
        # Access recommendation API
        return ApiClient.Recommendations(self)
