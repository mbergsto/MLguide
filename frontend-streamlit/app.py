from __future__ import annotations

import streamlit as st

from api import ApiClient, ApiConfig, ApiError
from models import RecommendationListResponse, RecommendationRequest
import ui
from config import settings


@st.cache_data(ttl=settings.meta_cache_ttl_seconds, show_spinner=True)
# Load metadata for form options with caching to avoid redundant API calls on every interaction
def load_meta_cached(cfg: ApiConfig):
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


def main() -> None:
    # App-level config
    st.set_page_config(page_title="ML Method Recommender", layout="wide")

    # Base UI chrome
    cfg = ApiConfig()
    ui.render_sidebar(cfg.base_url)
    ui.render_page_header()

    # Load form metadata (cached)
    try:
        phases, clusters, paradigms, tasks, dataset_types, conditions, performance = load_meta_cached(cfg)
    except Exception as e:
        ui.render_error(e)
        st.stop()

    # Render form and capture user intent (submit vs. just rerun)
    payload, submitted = ui.render_form(
        phases=phases,
        clusters=clusters,
        paradigms=paradigms,
        tasks=tasks,
        dataset_types=dataset_types,
        conditions=conditions,
        performance=performance,
    )

    # Build request object from current form values
    req = RecommendationRequest.model_validate(payload)

    # On submit: fetch fresh recommendations and store them for later reruns
    if submitted:
        try:
            with st.spinner("Fetching recommendations..."):
                with ApiClient(cfg) as client:
                    data = client.recommendations.recommend(req)

            # Normalize API response to a list of RecommendationItem
            if isinstance(data, dict) and "results" in data:
                rows = RecommendationListResponse.model_validate(data).results
            else:
                rows = data

            # Persist results and request payload for navigation/details page
            st.session_state["last_rows"] = rows
            st.session_state["last_request_payload"] = req.model_dump(exclude_none=True)

        except ApiError as e:
            ui.render_error(e)
            st.stop()
        except Exception as e:
            ui.render_error(e)
            st.stop()

    # Reuse cached results when user interacts with the page (e.g., clicks a method)
    rows = st.session_state.get("last_rows", [])
    if not rows:
        return

    # Render recommendations and handle method selection
    selected_iri = ui.render_recommendations(rows)
    if selected_iri:
        # Persist selected approach and navigate to details page
        st.session_state["selected_approach_iri"] = selected_iri
        st.switch_page("pages/method_details.py", query_params={"approach_iri": selected_iri})
        st.stop()


if __name__ == "__main__":
    main()
