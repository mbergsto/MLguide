from __future__ import annotations

import streamlit as st

from api import ApiConfig, ApiError
from config import settings
from models import RecommendationRequest
from services import recommendations_service
import state_helpers as state
from ui import home_page_ui as ui


@st.cache_data(ttl=settings.meta_cache_ttl_seconds, show_spinner=True)
def load_meta_cached(cfg: ApiConfig):
    # Load metadata for form options with caching to avoid redundant API calls.
    return recommendations_service.fetch_meta_options(cfg)


def main() -> None:
    st.set_page_config(page_title="MLguide 🤖", layout="wide")

    cfg = ApiConfig()
    ui.render_page_header()

    try:
        phases, clusters, paradigms, tasks, dataset_types, conditions, performance = load_meta_cached(cfg)
    except Exception as e:
        ui.render_error(e)
        st.stop()

    state.restore_form_state()

    payload, submitted = ui.render_form(
        phases=phases,
        clusters=clusters,
        paradigms=paradigms,
        tasks=tasks,
        dataset_types=dataset_types,
        conditions=conditions,
        performance=performance,
    )
    state.persist_form_state()

    req_payload = dict(payload)
    req_payload.setdefault("max_results", settings.max_results_default)
    req = RecommendationRequest.model_validate(req_payload)

    if submitted:
        try:
            with st.spinner("Fetching recommendations..."):
                rows = recommendations_service.fetch_recommendations(cfg, req)

            st.session_state["last_rows"] = rows
            st.session_state["last_request_payload"] = req.model_dump(exclude_none=True)
        except ApiError as e:
            ui.render_error(e)
            st.stop()
        except Exception as e:
            ui.render_error(e)
            st.stop()

    rows = st.session_state.get("last_rows", [])
    if not rows:
        return

    selected_iri = ui.render_recommendations(rows)
    if selected_iri:
        st.session_state["selected_approach_iri"] = selected_iri
        st.switch_page("pages/method_details.py", query_params={"approach_iri": selected_iri})
        st.stop()


if __name__ == "__main__":
    main()
