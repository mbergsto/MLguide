from __future__ import annotations

import json
from pathlib import Path

from integrations import github_notebook_client
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from integrations.api import ApiConfig, ApiError
from config.config import settings
from domain.models import ArticleItem, RecommendationRequest
from services import recommendations_service
from services.notebook_builder_service import build_notebook_json
from services.template_registry import resolve_template
from ui import method_details_ui as ui
from ui import nav_ui
from utils.utils import find_selected_row, get_method_label, to_template_method


st.set_page_config(page_title="MLguide 🤖 - Method details", layout="wide")

cfg = ApiConfig()
TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "notebooks"
ARTICLE_SEARCH_KEY = "details_article_search"
ARTICLE_SEARCH_CLEAR_KEY = "details_article_search_clear"


def _open_in_new_tab(url: str) -> None:
    payload = json.dumps(url)
    components.html(
        f"<script>window.open({payload}, '_blank');</script>",
        height=0,
        width=0,
    )


def _clear_article_search() -> None:
    st.session_state[ARTICLE_SEARCH_KEY] = ""


def _filter_articles(articles: list[ArticleItem], query: str) -> list[ArticleItem]:
    q = query.strip().lower()
    if not q:
        return articles
    return [
        article
        for article in articles
        if q in (article.label or "").lower() or q in (article.doi or "").lower()
    ]


@st.cache_data(ttl=settings.meta_cache_ttl_seconds, show_spinner=False)
def _load_meta_label_lookup(cfg: ApiConfig) -> dict[str, dict[str, str]]:
    phases, clusters, paradigms, tasks, dataset_types, conditions, performance = (
        recommendations_service.fetch_meta_options(cfg)
    )
    return {
        "phase": {o.iri: o.label for o in phases},
        "cluster": {o.iri: o.label for o in clusters},
        "paradigm": {o.iri: o.label for o in paradigms},
        "task": {o.iri: o.label for o in tasks},
        "dataset_type": {o.iri: o.label for o in dataset_types},
        "condition": {o.iri: o.label for o in conditions},
        "performance": {o.iri: o.label for o in performance},
    }


def _label_or_raw(lookup: dict[str, str], iri: str | None) -> str:
    if not iri:
        return "-"
    return lookup.get(iri, iri)


def _list_labels_or_raw(lookup: dict[str, str], iris: list[str] | None) -> str:
    if not iris:
        return "-"
    return ", ".join(lookup.get(iri, iri) for iri in iris)


def _build_request_context_items(
    request_payload: dict,
    lookup: dict[str, dict[str, str]],
) -> list[tuple[str, str]]:
    cluster_value = _list_labels_or_raw(lookup.get("cluster", {}), request_payload.get("cluster_iris"))

    return [
        ("Phase", _label_or_raw(lookup.get("phase", {}), request_payload.get("phase_iri"))),
        ("Cluster", cluster_value),
        ("Paradigm", _label_or_raw(lookup.get("paradigm", {}), request_payload.get("paradigm_iri"))),
        ("Task", _label_or_raw(lookup.get("task", {}), request_payload.get("task_iri"))),
        (
            "Dataset type",
            _label_or_raw(lookup.get("dataset_type", {}), request_payload.get("dataset_type_iri")),
        ),
        (
            "Conditions",
            _list_labels_or_raw(lookup.get("condition", {}), request_payload.get("conditions")),
        ),
        (
            "Performance prefs",
            _list_labels_or_raw(lookup.get("performance", {}), request_payload.get("performance_prefs")),
        ),
        ("Problem text", request_payload.get("problem_text") or "-"),
    ]


approach_iri = st.query_params.get("approach_iri")
payload = st.session_state.get("last_request_payload")

back_clicked = nav_ui.render_back_nav(key_prefix="details_nav")
if back_clicked:
    st.switch_page("home_page.py")
    st.stop()

if not approach_iri or not payload:
    st.switch_page("home_page.py")
    st.stop()

rows = st.session_state.get("last_rows", [])
selected_row = find_selected_row(rows, approach_iri)
method_label = get_method_label(selected_row)
method_title = method_label or "Selected method"

ui.render_page_title(method_title)

request_context_items: list[tuple[str, str]] = []
try:
    meta_lookup = _load_meta_label_lookup(cfg)
    request_context_items = _build_request_context_items(payload, meta_lookup)
except Exception:
    # Keep details usable even if metadata lookup fails.
    request_context_items = _build_request_context_items(payload, {})

template_method = to_template_method(method_title)
template_spec = resolve_template(template_method, TEMPLATE_ROOT)
if template_spec is None:
    ui.render_template_not_found(TEMPLATE_ROOT / "methods")
    st.stop()

template_path = TEMPLATE_ROOT / template_spec.template_path
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_ROOT)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

try:
    template = env.get_template(template_spec.template_path)
    rendered_code = template.render(
        method_key=template_method,
        method_title=method_title,
        problem_text=payload.get("problem_text"),
        target_column="target",
        family=template_spec.family,
    )
    notebook_json = build_notebook_json(method_title, rendered_code)
    has_colab_cfg = bool(settings.github_token and settings.notebooks_repo_name)

    colab_key = f"colab_url_{approach_iri}"
except TemplateNotFound:
    ui.render_template_not_found(template_path)
    st.stop()

req = RecommendationRequest.model_validate(payload)

try:
    details = recommendations_service.fetch_method_details(cfg, req, approach_iri)
except ApiError as e:
    ui.render_api_error(e)
    st.stop()

left_col, right_col = st.columns([1.65, 1.0], gap="large")

with left_col:
    ui.render_notebook_preview(rendered_code)
    open_colab_clicked = ui.render_template_actions(
        template_method=template_method,
        notebook_json=notebook_json,
        has_colab_cfg=has_colab_cfg,
    )
    if open_colab_clicked:
        try:
            with st.spinner("Uploading notebook to GitHub..."):
                colab_url = github_notebook_client.upload_notebook_and_get_colab_url(
                    notebook_json=notebook_json,
                    method_key=template_method or "method",
                    token=settings.github_token,
                    repo_name=settings.notebooks_repo_name,
                    branch=settings.notebooks_repo_branch,
                )
                st.session_state[colab_key] = colab_url
                _open_in_new_tab(colab_url)
        except Exception as e:
            ui.render_colab_error(e)

    if not has_colab_cfg:
        ui.render_colab_config_hint()

with right_col:
    ui.render_context_panel(request_context_items)
    ui.render_supporting_articles_header()
    article_query = ui.render_articles_search_controls(
        search_key=ARTICLE_SEARCH_KEY,
        clear_key=ARTICLE_SEARCH_CLEAR_KEY,
        on_clear=_clear_article_search,
    )
    filtered_articles = _filter_articles(details.articles, article_query)
    ui.render_supporting_articles(filtered_articles)
