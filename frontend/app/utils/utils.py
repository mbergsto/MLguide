from __future__ import annotations

import re
from typing import Any


def to_template_method(value: str | None) -> str:
    if not value:
        return ""

    key = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    aliases = {
        "randomforest": "random_forest",
        "random_forest_classifier": "random_forest",
        "support_vector_machine": "svm",
        "svc": "svm",
        "s_v_m": "svm",
        "k_nearest_neighbors": "knn",
        "k_nearest_neighbours": "knn",
        "kneighborsclassifier": "knn",
    }
    return aliases.get(key, key)


def find_selected_row(rows: list[Any], approach_iri: str) -> Any | None:
    return next(
        (
            row
            for row in rows
            if (getattr(row, "approach", None) if not isinstance(row, dict) else row.get("approach"))
            == approach_iri
        ),
        None,
    )


def get_method_label(row: Any | None) -> str | None:
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get("methodLabel")
    return getattr(row, "methodLabel", None)


def build_doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}"
