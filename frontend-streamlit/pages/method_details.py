from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template

from api import ApiConfig, ApiError
from config import settings
from models import RecommendationRequest
from services import notebook_service, recommendations_service
from ui import method_details_ui as ui
from ui import nav_ui
from utils import build_notebook_json, find_selected_row, get_method_label, to_template_method


st.set_page_config(page_title="MLguide 🤖 - Method details", layout="wide")

cfg = ApiConfig()
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "scikit-learn" / "template_test.jinja"


def _open_in_new_tab(url: str) -> None:
    payload = json.dumps(url)
    components.html(
        f"<script>window.open({payload}, '_blank');</script>",
        height=0,
        width=0,
    )


approach_iri = st.query_params.get("approach_iri")
payload = st.session_state.get("last_request_payload")

back_clicked = nav_ui.render_back_nav(key_prefix="details_nav")
if back_clicked:
    st.switch_page("home_page.py")
    st.stop()

if not approach_iri or not payload:
    ui.render_missing_navigation_state()
    st.stop()

rows = st.session_state.get("last_rows", [])
selected_row = find_selected_row(rows, approach_iri)
method_label = get_method_label(selected_row)
method_title = method_label or "Selected method"

ui.render_page_title(method_title)

if TEMPLATE_PATH.exists():
    raw_template = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(raw_template)
    template_method = to_template_method(method_title)
    rendered_code = template.render(method=template_method)
    has_colab_cfg = bool(settings.github_token and settings.notebooks_repo_name)

    open_colab_clicked = ui.render_template_section(rendered_code, template_method, has_colab_cfg)

    notebook_json = build_notebook_json(method_title, rendered_code)
    colab_key = f"colab_url_{approach_iri}"

    if open_colab_clicked:
        try:
            with st.spinner("Uploading notebook to GitHub..."):
                colab_url = notebook_service.upload_notebook_and_get_colab_url(
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
else:
    ui.render_template_not_found(TEMPLATE_PATH)

req = RecommendationRequest.model_validate(payload)

try:
    details = recommendations_service.fetch_method_details(cfg, req, approach_iri)
    ui.render_supporting_articles(details.articles)
except ApiError as e:
    ui.render_api_error(e)
    st.stop()
