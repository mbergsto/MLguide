from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class TemplateSpec:
    family: str
    template_path: str


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


@lru_cache(maxsize=8)
def _discover_method_templates(template_root: Path) -> dict[str, TemplateSpec]:
    methods_root = template_root / "methods"
    discovered: dict[str, TemplateSpec] = {}
    for file_path in methods_root.rglob("*.py.jinja"):
        relative = file_path.relative_to(template_root)
        parts = relative.parts
        if len(parts) < 3:
            continue

        _, family, filename = parts[0], parts[1], parts[2]
        method_key = filename.removesuffix(".py.jinja")
        if method_key == "default":
            continue

        discovered[method_key] = TemplateSpec(
            family=family,
            template_path=relative.as_posix(),
        )
    return discovered


def resolve_template(method_key: str, template_root: Path) -> TemplateSpec | None:
    discovered = _discover_method_templates(template_root)
    known = discovered.get(method_key)
    if known is not None:
        return known

    family = infer_method_family(method_key)
    fallback = TemplateSpec(
        family=family,
        template_path=_FAMILY_FALLBACK_TEMPLATE[family],
    )
    if (template_root / fallback.template_path).exists():
        return fallback
    return None
