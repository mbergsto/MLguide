from __future__ import annotations

import streamlit as st


FORM_STATE_KEYS = [
    "hp_phase",
    "hp_cluster",
    "hp_paradigm",
    "hp_task",
    "hp_dataset_type",
    "hp_conditions",
    "hp_performance",
    "hp_problem_text",
]
FORM_MEMORY_KEY = "hp_form_memory"


def ensure_single_select_state(key: str, valid_values: list[str], default_value: str) -> None:
    current = st.session_state.get(key)
    if current not in valid_values:
        st.session_state[key] = default_value


def ensure_multi_select_state(key: str, valid_values: set[str]) -> None:
    current = st.session_state.get(key, [])
    if not isinstance(current, list):
        st.session_state[key] = []
        return
    st.session_state[key] = [v for v in current if v in valid_values]


def restore_form_state() -> None:
    snapshot = st.session_state.get(FORM_MEMORY_KEY)
    if not isinstance(snapshot, dict):
        return

    for key in FORM_STATE_KEYS:
        if key not in st.session_state and key in snapshot:
            value = snapshot[key]
            st.session_state[key] = list(value) if isinstance(value, list) else value


def persist_form_state() -> None:
    snapshot: dict[str, object] = {}
    for key in FORM_STATE_KEYS:
        if key in st.session_state:
            value = st.session_state[key]
            snapshot[key] = list(value) if isinstance(value, list) else value
    st.session_state[FORM_MEMORY_KEY] = snapshot


def reset_home_state() -> None:
    st.session_state.pop("last_rows", None)
    st.session_state.pop("last_request_payload", None)
    st.session_state.pop("selected_approach_iri", None)
    st.session_state.pop(FORM_MEMORY_KEY, None)
    for key in FORM_STATE_KEYS:
        st.session_state.pop(key, None)
