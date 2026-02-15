from __future__ import annotations

import streamlit as st

from models import Option, RecommendationItem, RecommendationDetailsResponse


def render_page_header() -> None:
    st.title("ML Method Recommender")
    st.caption("Ranked ML methods based on article evidence and ontology rules.")


def render_sidebar(base_url: str) -> None:
    with st.sidebar:
        st.subheader("Settings")
        st.text_input("Backend URL", value=base_url, disabled=True)
        st.divider()
        st.caption("Set BACKEND_URL to change this.")


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
    with st.form("recommend_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            phase = _select_option("Lifecycle phase", phases)
            cluster = _select_option("Application cluster", clusters)
            paradigm = _select_option("Learning paradigm", paradigms)

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

        problem_text = st.text_area("Problem description (optional)", height=110)
        submitted = st.form_submit_button("Get recommendations")

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


def render_recommendations_table(rows: list[RecommendationItem]) -> None:
    st.subheader("Recommendations")

    if not rows:
        st.info("No methods found for the selected inputs.")
        return

    data = []
    for r in rows:
        data.append(
            {
                "Method": r.methodLabel or r.method or "",
                "Approach": r.approachLabel or r.approach or "",
                "Articles": r.supportingArticles,
                "Possible-if": r.possibleIfMatches,
                "Performance": r.performanceMatches,
                "Task": r.taskMatch,
            }
        )
    st.dataframe(data, use_container_width=True)


def render_details(details: RecommendationDetailsResponse) -> None:
    st.subheader("Details")
    st.markdown(f"**Approach IRI:** `{details.approachIri}`")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Condition matches**")
        st.write([o.label for o in details.matches.conditions] or "—")
    with c2:
        st.markdown("**Performance matches**")
        st.write([o.label for o in details.matches.performance] or "—")
    with c3:
        st.markdown("**Task matches**")
        st.write([o.label for o in details.matches.tasks] or "—")

    st.markdown("**Supporting articles**")
    if not details.articles:
        st.write("—")
    else:
        for a in details.articles:
            label = a.label or a.doi
            st.write(f"- {label} (DOI: {a.doi})")


def render_error(e: Exception) -> None:
    st.error("Request failed.")
    st.exception(e)
