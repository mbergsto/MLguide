from __future__ import annotations

import streamlit as st

from models import Option, RecommendationItem
from state_helpers import ensure_multi_select_state, ensure_single_select_state


def render_page_header() -> None:
    # Main page header
    st.title("MLguide 🤖")
    st.caption("Fill in the form and review recommended ML methods for your problem.")


def _option_maps(options: list[Option]) -> tuple[list[str], dict[str, str]]:
    iris = [o.iri for o in options]
    labels = {o.iri: o.label for o in options}
    return iris, labels


def render_form(
    phases: list[Option],
    clusters: list[Option],
    paradigms: list[Option],
    tasks: list[Option],
    dataset_types: list[Option],
    conditions: list[Option],
    performance: list[Option],
) -> tuple[dict, bool]:
    phase_iris, phase_labels = _option_maps(phases)
    cluster_iris, cluster_labels = _option_maps(clusters)
    paradigm_iris, paradigm_labels = _option_maps(paradigms)
    task_iris, task_labels = _option_maps(tasks)
    dataset_iris, dataset_labels = _option_maps(dataset_types)
    condition_iris, condition_labels = _option_maps(conditions)
    performance_iris, performance_labels = _option_maps(performance)

    ensure_single_select_state("hp_phase", phase_iris, phase_iris[0])
    ensure_single_select_state("hp_cluster", cluster_iris, cluster_iris[0])
    ensure_single_select_state("hp_paradigm", paradigm_iris, paradigm_iris[0])
    ensure_single_select_state("hp_task", [""] + task_iris, "")
    ensure_single_select_state("hp_dataset_type", [""] + dataset_iris, "")
    ensure_multi_select_state("hp_conditions", set(condition_iris))
    ensure_multi_select_state("hp_performance", set(performance_iris))

    # Form groups all inputs and only triggers on submit
    with st.form("recommend_form"):
        c1, c2, c3 = st.columns(3)

        # Core categorical selections
        with c1:
            phase_iri = st.selectbox(
                "Lifecycle phase",
                options=phase_iris,
                format_func=lambda iri: phase_labels[iri],
                key="hp_phase",
            )
            cluster_iri = st.selectbox(
                "Application cluster",
                options=cluster_iris,
                format_func=lambda iri: cluster_labels[iri],
                key="hp_cluster",
            )
            paradigm_iri = st.selectbox(
                "Learning paradigm",
                options=paradigm_iris,
                format_func=lambda iri: paradigm_labels[iri],
                key="hp_paradigm",
            )

        # Optional task and dataset context
        with c2:
            task_iri = st.selectbox(
                "Task (optional)",
                options=[""] + task_iris,
                format_func=lambda iri: "—" if iri == "" else task_labels[iri],
                key="hp_task",
            )
            dataset_type_iri = st.selectbox(
                "Dataset type (optional)",
                options=[""] + dataset_iris,
                format_func=lambda iri: "—" if iri == "" else dataset_labels[iri],
                key="hp_dataset_type",
            )

        # Multi-select filters and preferences
        with c3:
            cond_selected_iris = st.multiselect(
                "Conditions",
                options=condition_iris,
                format_func=lambda iri: condition_labels[iri],
                key="hp_conditions",
            )
            perf_selected_iris = st.multiselect(
                "Performance preferences",
                options=performance_iris,
                format_func=lambda iri: performance_labels[iri],
                key="hp_performance",
            )

        # Free-text problem description
        problem_text = st.text_area("Problem description (optional)", height=110, key="hp_problem_text")

        # Submit button returns True only in the submit rerun
        submitted = st.form_submit_button("Get recommendations")

    # Normalize form values into API payload
    payload = {
        "problem_text": problem_text.strip() or None,
        "phase_iri": phase_iri,
        "cluster_iri": cluster_iri,
        "paradigm_iri": paradigm_iri,
        "task_iri": None if task_iri == "" else task_iri,
        "conditions": cond_selected_iris,
        "performance_prefs": perf_selected_iris,
        "dataset_type_iri": None if dataset_type_iri == "" else dataset_type_iri,
    }

    return payload, submitted


def render_recommendations(rows: list[RecommendationItem]) -> str | None:
    # Section header
    st.subheader("Recommendations")
    st.caption("Click a method to see more details.")

    # Empty state
    if not rows:
        st.info("No methods found for the selected inputs.")
        return None
    
    # Column headers
    hcols = st.columns([3, 3, 1, 1, 1])
    hcols[0].markdown("")
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
