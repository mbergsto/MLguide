from __future__ import annotations

import streamlit as st

from models import Option, RecommendationItem, RecommendationDetailsResponse


def render_page_header() -> None:
    # Main page header
    st.title("ML Method Recommender")
    st.caption("Ranked ML methods based on article evidence and ontology rules.")


def render_sidebar(base_url: str) -> None:
    # Sidebar with static settings/info
    with st.sidebar:
        st.subheader("Settings")
        st.text_input("Backend URL", value=base_url, disabled=True)
        

def _select_option(label: str, options: list[Option]) -> Option:
    return st.selectbox(label, options=options, format_func=lambda o: o.label)


def render_form(
    phases: list[Option],
    clusters: list[Option],
    paradigms: list[Option],
    tasks: list[Option],
    dataset_types: list[Option],
    conditions: list[Option],
    performance: list[Option],
) -> tuple[dict, bool]:
    # Form groups all inputs and only triggers on submit
    with st.form("recommend_form"):
        c1, c2, c3 = st.columns(3)

        # Core categorical selections
        with c1:
            phase = _select_option("Lifecycle phase", phases)
            cluster = _select_option("Application cluster", clusters)
            paradigm = _select_option("Learning paradigm", paradigms)

        # Optional task and dataset context
        with c2:
            task = st.selectbox(
                "Task (optional)",
                options=[None] + tasks,
                format_func=lambda o: "—" if o is None else o.label,
            )
            dataset_type = st.selectbox(
                "Dataset type (optional)",
                options=[None] + dataset_types,
                format_func=lambda o: "—" if o is None else o.label,
            )

        # Multi-select filters and preferences
        with c3:
            cond_selected = st.multiselect(
                "Conditions",
                options=conditions,
                format_func=lambda o: o.label,
            )
            perf_selected = st.multiselect(
                "Performance preferences",
                options=performance,
                format_func=lambda o: o.label,
            )

        # Free-text problem description
        problem_text = st.text_area("Problem description (optional)", height=110)

        # Submit button returns True only in the submit rerun
        submitted = st.form_submit_button("Get recommendations")

    # Normalize form values into API payload
    payload = {
        "problem_text": problem_text.strip() or None,
        "phase_iri": phase.iri,
        "cluster_iri": cluster.iri,
        "paradigm_iri": paradigm.iri,
        "task_iri": None if task is None else task.iri,
        "conditions": [o.iri for o in cond_selected],
        "performance_prefs": [o.iri for o in perf_selected],
        "dataset_type_iri": None if dataset_type is None else dataset_type.iri,
    }

    return payload, submitted


def render_recommendations(rows: list[RecommendationItem]) -> str | None:
    # Section header
    st.subheader("Recommendations")

    # Empty state
    if not rows:
        st.info("No methods found for the selected inputs.")
        return None
    
    # Column headers
    hcols = st.columns([3, 3, 1, 1, 1])
    hcols[0].markdown("**Method**")
    # hcols[1].markdown("**Approach**")
    hcols[2].markdown("**Articles**")
    hcols[3].markdown("**Perf.**")
    hcols[4].markdown("**Task**")

    # Render each recommendation as a row with an action button
    for r in rows:
        method_label = r.methodLabel or r.method or "Unnamed method"
        cols = st.columns([3, 3, 1, 1, 1])

        with cols[0]:
            # Button returns True in the rerun where it is clicked
            clicked = st.button(method_label, key=f"method_{r.approach}")
        # with cols[1]:
        #     st.write(r.approachLabel or r.approach or "")
        with cols[2]:
            st.write(r.supportingArticles)
        with cols[3]:
            st.write(r.performanceMatches)
        with cols[4]:
            st.write(r.taskMatch)

        # Return the selected approach identifier
        if clicked:
            return r.approach

    return None


def render_error(e: Exception) -> None:
    st.error("Request failed.")
    st.exception(e)
