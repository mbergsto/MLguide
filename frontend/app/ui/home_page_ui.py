from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import streamlit as st

from domain.models import Option, RecommendationItem
from utils.state_helpers import ensure_multi_select_state, ensure_single_select_state


CLUSTER_KEYWORD_BLOCKLIST_PATH = Path(__file__).resolve().parents[1] / "config" / "cluster_keyword_blocklist.txt"
PARADIGM_GUIDE_SKIP = "Not sure / skip"
PARADIGM_GUIDE_SUPERVISED = "**Supervised Learning**: I have historical data with with known outcomes (labels) that I want to predict or classify"
PARADIGM_GUIDE_UNSUPERVISED = "**Unsupervised Learning**: The goal is to explore patterns, group similar cases, or detect anomalies without specific known outcomes (labels)"
PARADIGM_GUIDE_REINFORCEMENT = "**Reinforcement Learning**: The problem involves learning decisions over time based on feedback or rewards"
PARADIGM_GUIDE_OPTIONS = [
    PARADIGM_GUIDE_SKIP,
    PARADIGM_GUIDE_SUPERVISED,
    PARADIGM_GUIDE_UNSUPERVISED,
    PARADIGM_GUIDE_REINFORCEMENT,
]


def render_page_header() -> None:
    # Main page header
    st.title("MLguide 🤖")
    st.caption("Fill in the form and review recommended ML methods for your problem.")


def _option_maps(options: list[Option]) -> tuple[list[str], dict[str, str]]:
    iris = [o.iri for o in options]
    labels = {o.iri: o.label for o in options}
    return iris, labels


def _contains_any(text: str, candidates: tuple[str, ...]) -> bool:
    text_l = text.lower()
    return any(candidate in text_l for candidate in candidates)


def _load_cluster_keyword_blocklist() -> set[str]:
    try:
        raw = CLUSTER_KEYWORD_BLOCKLIST_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return set()

    blocked: set[str] = set()
    for line in raw.splitlines():
        token = line.strip()
        if not token or token.startswith("#"):
            continue
        blocked.add(token.casefold())
    return blocked


def _suggest_paradigm_iri(paradigms: list[Option], guide_choice: str) -> str | None:
    for option in paradigms:
        label = option.label.lower()
        if guide_choice == PARADIGM_GUIDE_SUPERVISED and _contains_any(
            label, ("supervised",)
        ):
            return option.iri
        if guide_choice == PARADIGM_GUIDE_UNSUPERVISED and _contains_any(
            label, ("unsupervised",)
        ):
            return option.iri
        if guide_choice == PARADIGM_GUIDE_REINFORCEMENT and _contains_any(
            label, ("reinforcement",)
        ):
            return option.iri
    return None


def _cluster_keyword_metadata(clusters: list[Option]) -> tuple[list[str], dict[str, set[str]], dict[str, set[str]]]:
    blocked_keywords = _load_cluster_keyword_blocklist()
    keyword_order: list[str] = []
    keyword_display_by_norm: dict[str, str] = {}
    keyword_to_cluster_iris: dict[str, set[str]] = defaultdict(set)
    cluster_keywords_by_iri: dict[str, set[str]] = defaultdict(set)

    for cluster in clusters:
        # Cluster labels are expected to be comma-separated keywords.
        for raw_keyword in cluster.label.split(","):
            keyword = raw_keyword.strip()
            if not keyword:
                continue
            norm = keyword.casefold()
            if norm in blocked_keywords:
                continue
            display = keyword_display_by_norm.get(norm)
            if display is None:
                keyword_display_by_norm[norm] = keyword
                keyword_order.append(keyword)
                display = keyword
            keyword_to_cluster_iris[display].add(cluster.iri)
            cluster_keywords_by_iri[cluster.iri].add(norm)

    return keyword_order, keyword_to_cluster_iris, cluster_keywords_by_iri


def _render_cluster_keyword_picker(
    clusters: list[Option],
    cluster_iris: list[str],
    cluster_labels: dict[str, str],
) -> list[str]:
    keywords, keyword_to_cluster_iris, cluster_keywords_by_iri = _cluster_keyword_metadata(clusters)
    if not keywords:
        return cluster_iris

    st.subheader("Help the MLguide by describing your problem")
    st.caption(
        "Pick keywords that describe the problem. This will help the MLguide prioritize methods that are relevant to your problem context. You can select multiple keywords, or skip if you're not sure."
    )

    if hasattr(st, "pills"):
        selected_keywords = st.pills(
            "Cluster keywords",
            options=keywords,
            selection_mode="multi",
            key="hp_cluster_keywords",
            label_visibility="collapsed",
        )
    else:
        selected_keywords = st.multiselect(
            "Cluster keywords",
            options=keywords,
            key="hp_cluster_keywords",
            label_visibility="collapsed",
        )

    if not selected_keywords:
        return cluster_iris

    selected_norms = {keyword.casefold() for keyword in selected_keywords}
    scored: list[tuple[int, str, str]] = []
    for iri in cluster_iris:
        overlap = len(cluster_keywords_by_iri.get(iri, set()) & selected_norms)
        if overlap > 0:
            scored.append((-overlap, cluster_labels.get(iri, "").lower(), iri))

    if not scored:
        st.info("No cluster labels matched the selected keywords. Showing all clusters.")
        return cluster_iris

    matched_cluster_iris = [iri for _, _, iri in sorted(scored)]
    return matched_cluster_iris


def _render_paradigm_guidance(paradigms: list[Option], paradigm_labels: dict[str, str]) -> None:
    if not paradigms:
        return

    guide_choice = st.radio(
        "Which setup best matches your problem?",
        options=PARADIGM_GUIDE_OPTIONS,
        key="hp_paradigm_guide",
    )
    if guide_choice == PARADIGM_GUIDE_SKIP:
        st.session_state["hp_paradigm"] = ""
        return

    suggested_iri = _suggest_paradigm_iri(paradigms, guide_choice)
    if not suggested_iri:
        st.caption("No direct paradigm match found from labels. You can choose manually below.")
        return

    st.caption(f"Suggested paradigm: `{paradigm_labels[suggested_iri]}`")
    st.session_state["hp_paradigm"] = suggested_iri


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

    cluster_select_iris = _render_cluster_keyword_picker(clusters, cluster_iris, cluster_labels)
    cluster_override = st.session_state.pop("hp_cluster_iris_override", None)
    if isinstance(cluster_override, list):
        cluster_select_iris = [str(v) for v in cluster_override]

    _render_paradigm_guidance(paradigms, paradigm_labels)

    # Lifecycle phase selection is temporarily disabled.
    # Keep state logic commented so it is easy to restore later.
    # ensure_single_select_state("hp_phase", phase_iris, phase_iris[0] if phase_iris else "")
    ensure_single_select_state("hp_paradigm", [""] + paradigm_iris, "")
    ensure_single_select_state("hp_task", [""] + task_iris, "")
    ensure_single_select_state("hp_dataset_type", [""] + dataset_iris, "")
    ensure_multi_select_state("hp_conditions", set(condition_iris))
    ensure_multi_select_state("hp_performance", set(performance_iris))

    # Form groups all inputs and only triggers on submit
    with st.form("recommend_form"):
        c1, c2, c3 = st.columns(3)

        # Core categorical selections
        with c1:
            # Lifecycle phase selection is temporarily disabled.
            # phase_iri = st.selectbox(
            #     "Lifecycle phase",
            #     options=phase_iris,
            #     format_func=lambda iri: phase_labels[iri],
            #     key="hp_phase",
            # )
            paradigm_iri = st.selectbox(
                "Learning paradigm",
                options=[""] + paradigm_iris,
                format_func=lambda iri: "—" if iri == "" else paradigm_labels[iri],
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
        # "phase_iri": phase_iri,
        "phase_iri": None,
        "cluster_iris": cluster_select_iris,
        "paradigm_iri": None if paradigm_iri == "" else paradigm_iri,
        "task_iri": None if task_iri == "" else task_iri,
        "conditions": cond_selected_iris,
        "performance_prefs": perf_selected_iris,
        "dataset_type_iri": None if dataset_type_iri == "" else dataset_type_iri,
    }

    return payload, submitted


def render_recommendations(rows: list[RecommendationItem]) -> str | None:
    # Section header
    st.subheader("Possible ML Methods")
    st.caption("Click on a method to see more details.")

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
