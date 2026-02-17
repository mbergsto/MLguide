import streamlit as st
from jinja2 import Template
from pathlib import Path
import re
from api import ApiClient, ApiConfig, ApiError
from models import RecommendationRequest

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
