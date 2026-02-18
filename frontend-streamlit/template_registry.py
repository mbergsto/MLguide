from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateSpec:
    family: str
    template_path: str


_METHOD_TEMPLATE_MAP: dict[str, TemplateSpec] = {
    "random_forest": TemplateSpec(
        family="classification",
        template_path="methods/classification/random_forest.py.jinja",
    ),
    "svm": TemplateSpec(
        family="classification",
        template_path="methods/classification/svm.py.jinja",
    ),
    "linear_regression": TemplateSpec(
        family="regression",
        template_path="methods/regression/linear_regression.py.jinja",
    ),
}

_REGRESSION_HINTS = {
    "linear_regression",
    "ridge",
    "lasso",
    "elastic_net",
    "random_forest_regressor",
    "xgboost_regressor",
}

_FAMILY_FALLBACK_TEMPLATE: dict[str, str] = {
    "classification": "methods/classification/default.py.jinja",
    "regression": "methods/regression/default.py.jinja",
}


def infer_method_family(method_key: str) -> str:
    if method_key in _REGRESSION_HINTS:
        return "regression"
    if "regression" in method_key or "regressor" in method_key:
        return "regression"
    return "classification"


def resolve_template(method_key: str) -> TemplateSpec:
    known = _METHOD_TEMPLATE_MAP.get(method_key)
    if known:
        return known

    family = infer_method_family(method_key)
    return TemplateSpec(
        family=family,
        template_path=_FAMILY_FALLBACK_TEMPLATE[family],
    )
