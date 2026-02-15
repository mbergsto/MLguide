from __future__ import annotations

import streamlit as st

from api import ApiClient, ApiConfig, ApiError
from models import RecommendationListResponse, RecommendationRequest
import ui


@st.cache_data(ttl=3600)
def load_meta_cached(base_url: str, timeout_seconds: float):
    with ApiClient(ApiConfig(base_url=base_url, timeout_seconds=timeout_seconds)) as client:
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
    st.set_page_config(page_title="ML Method Recommender", layout="wide")

    cfg = ApiConfig()
    ui.render_sidebar(cfg.base_url)
    ui.render_page_header()

    try:
        phases, clusters, paradigms, tasks, dataset_types, conditions, performance = load_meta_cached(
            cfg.base_url, cfg.timeout_seconds
        )
    except Exception as e:
        ui.render_error(e)
        st.stop()

    payload, submitted = ui.render_form(
        phases=phases,
        clusters=clusters,
        paradigms=paradigms,
        tasks=tasks,
        dataset_types=dataset_types,
        conditions=conditions,
        performance=performance,
    )

    if not submitted:
        return

    req = RecommendationRequest.model_validate(payload)

    try:
        with st.spinner("Fetching recommendations..."):
            with ApiClient(cfg) as client:
                data = client.recommendations.recommend(req)

        if isinstance(data, dict) and "results" in data:
            rows = RecommendationListResponse.model_validate(data).results
        else:
            rows = data

        ui.render_recommendations_table(rows)

        st.divider()
        st.subheader("Get details for one approach")

        approach_iri = st.text_input(
            "Approach IRI",
            value="",
            placeholder="Paste an approach IRI from the results",
        )

        if st.button("Fetch details", disabled=not approach_iri.strip()):
            with st.spinner("Fetching details..."):
                with ApiClient(cfg) as client:
                    details = client.recommendations.details(req, approach_iri.strip())
            ui.render_details(details)

    except ApiError as e:
        ui.render_error(e)
    except Exception as e:
        ui.render_error(e)


if __name__ == "__main__":
    main()
