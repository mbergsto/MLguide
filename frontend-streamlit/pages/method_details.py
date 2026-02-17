import base64
import json
from datetime import datetime, timezone
import streamlit as st
from jinja2 import Template
from pathlib import Path
import re
import httpx
from api import ApiClient, ApiConfig, ApiError
from models import RecommendationRequest
from config import settings


st.set_page_config(page_title="Method details", layout="wide")

cfg = ApiConfig()
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "scikit-learn" / "template_test.jinja"


def _to_template_method(value: str | None) -> str:
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


def _build_notebook_json(method_title: str, python_code: str) -> str:
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {method_title}\n", "Generated from ML catalogue template.\n"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": python_code.splitlines(keepends=True),
            },
        ],
        "metadata": {
            "colab": {"name": f"{method_title}.ipynb"},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, ensure_ascii=False, indent=2)


def _upload_notebook_and_get_colab_url(notebook_json: str, method_key: str) -> str:
    token = settings.github_token
    repo_name = settings.notebooks_repo_name
    branch = settings.notebooks_repo_branch

    if not token or not repo_name:
        raise RuntimeError("Missing GITHUB_TOKEN or NOTEBOOKS_REPO_NAME.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = f"notebooks/{method_key or 'method'}_{timestamp}.ipynb"
    api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    payload = {
        "message": f"Add generated notebook for {method_key or 'method'}",
        "content": base64.b64encode(notebook_json.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    res = httpx.put(api_url, headers=headers, json=payload, timeout=30.0)
    if res.is_error:
        detail = res.text[:400] if res.text else f"status={res.status_code}"
        raise RuntimeError(f"GitHub upload failed: {detail}")

    return f"https://colab.research.google.com/github/{repo_name}/blob/{branch}/{file_path}"

# Read navigation state
approach_iri = st.query_params.get("approach_iri")
payload = st.session_state.get("last_request_payload")

# Missing navigation state
if not approach_iri or not payload:
    st.title("Method details")
    st.info("Failed to load method details. Go back to recommendations.")
    st.stop()

# Resolve selected method labels from stored recommendations
rows = st.session_state.get("last_rows", [])
selected_row = next(
    (
        r
        for r in rows
        if (getattr(r, "approach", None) if not isinstance(r, dict) else r.get("approach")) == approach_iri
    ),
    None,
)
method_label = (
    (getattr(selected_row, "methodLabel", None) if selected_row and not isinstance(selected_row, dict) else selected_row.get("methodLabel"))
    if selected_row
    else None
)

method_title = method_label or "Selected method"

st.title(f"Method details: {method_title}")

# Render and expose a downloadable template for the selected method
if TEMPLATE_PATH.exists():
    raw_template = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(raw_template)
    template_method = _to_template_method(method_title)
    rendered_code = template.render(method=template_method)

    st.subheader("Generated scikit-learn template")
    st.caption(f"Template method key: `{template_method or 'unknown'}`")
    st.code(rendered_code, language="python")
    st.download_button(
        label="Download generated template (.py)",
        data=rendered_code,
        file_name=f"{template_method or 'method'}_template.py",
        mime="text/x-python",
    )

    notebook_json = _build_notebook_json(method_title, rendered_code)
    colab_key = f"colab_url_{approach_iri}"
    has_colab_cfg = bool(settings.github_token and settings.notebooks_repo_name)

    if st.button("Open in Colab", type="primary", disabled=not has_colab_cfg):
        try:
            with st.spinner("Uploading notebook to GitHub..."):
                # Debug
                token = settings.github_token or ""
                st.write("token length:", len(token.strip()))
                st.write("token prefix:", token.strip()[:4])   # bare 4 tegn
                st.write("repo_name:", settings.notebooks_repo_name)
                # Debug

                st.session_state[colab_key] = _upload_notebook_and_get_colab_url(
                    notebook_json=notebook_json,
                    method_key=template_method or "method",
                )
        except Exception as e:
            st.error(f"Could not create Colab link: {e}")

    if not has_colab_cfg:
        st.caption("Set `GITHUB_TOKEN` and `NOTEBOOKS_REPO_NAME` to enable Colab export.")

    colab_url = st.session_state.get(colab_key)
    if colab_url:
        st.link_button("Launch in Colab", colab_url)
else:
    st.warning(f"Template file not found: {TEMPLATE_PATH}")

# Rebuild request from stored payload
req = RecommendationRequest.model_validate(payload)

try:
    # Fetch details from backend
    with ApiClient(cfg) as client:
        details = client.recommendations.details(req, approach_iri)

    st.subheader("Supporting articles")

    # Empty state
    if not details.articles:
        st.write("—")
        st.stop()

    # Render article list with clickable DOI links
    for a in details.articles:
        title = a.label or "Untitled article"
        doi_url = f"https://doi.org/{a.doi}"
        st.markdown(f"- **{title}** — [{a.doi}]({doi_url})")

except ApiError as e:
    st.error(f"{e} ({e.status})")
    st.stop()
