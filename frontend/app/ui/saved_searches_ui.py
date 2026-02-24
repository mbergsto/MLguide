from __future__ import annotations

from datetime import datetime

import streamlit as st

from domain.models import SavedSearch, SavedSearchPayload
from integrations.api import ApiClient, ApiConfig, ApiError
from ui.sidebar_auth_ui import AUTH_USER_KEY


SIDEBAR_SAVED_SEARCHES_ERROR_KEY = "sidebar_saved_searches_error"
SIDEBAR_SAVED_SEARCHES_INFO_KEY = "sidebar_saved_searches_info"
SIDEBAR_SAVED_SEARCHES_LOAD_SELECT_KEY = "sidebar_saved_searches_load_select"
AUTO_FETCH_AFTER_SAVED_SEARCH_LOAD_KEY = "auto_fetch_after_saved_search_load"


def _current_user_id() -> int | None:
    user = st.session_state.get(AUTH_USER_KEY)
    if not isinstance(user, dict):
        return None
    user_id = user.get("id")
    return user_id if isinstance(user_id, int) else None


def _format_saved_time(raw: str) -> str:
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return raw


def _saved_search_label(search: SavedSearch) -> str:
    task = search.task_iri or "no-task"
    text = (search.problem_text or "").strip()
    snippet = (text[:28] + "...") if len(text) > 28 else (text or "no-description")
    return f"#{search.id} | {task} | {snippet}"


def _apply_saved_search_to_home_form(search: SavedSearch) -> None:
    st.session_state["hp_paradigm_guide"] = "Not sure / skip"
    st.session_state["hp_cluster_keywords"] = []
    st.session_state["hp_phase"] = search.phase_iri or ""
    st.session_state["hp_paradigm"] = search.paradigm_iri or ""
    st.session_state["hp_task"] = search.task_iri or ""
    st.session_state["hp_dataset_type"] = search.dataset_type_iri or ""
    st.session_state["hp_conditions"] = list(search.conditions or [])
    st.session_state["hp_performance"] = list(search.performance_prefs or [])
    st.session_state["hp_problem_text"] = search.problem_text or ""
    # Cluster selection is derived in the UI and has no direct widget. Use a one-shot override.
    st.session_state["hp_cluster_iris_override"] = list(search.cluster_iris or [])
    st.session_state[AUTO_FETCH_AFTER_SAVED_SEARCH_LOAD_KEY] = True

    st.session_state.pop("last_rows", None)
    st.session_state.pop("last_request_payload", None)
    st.session_state.pop("selected_approach_iri", None)


def render_save_search_action(cfg: ApiConfig, search_payload: dict) -> None:
    user_id = _current_user_id()
    if user_id is None:
        return

    st.caption("Logged in users can save this search for later.")
    if not st.button("Save this search", key="save_current_search_button"):
        return

    payload = SavedSearchPayload.model_validate(search_payload)

    try:
        with ApiClient(cfg) as client:
            saved = client.users.save_search(user_id=user_id, payload=payload)
        st.session_state[SIDEBAR_SAVED_SEARCHES_INFO_KEY] = f"Saved search #{saved.id}"
        st.session_state.pop(SIDEBAR_SAVED_SEARCHES_ERROR_KEY, None)
        st.rerun()
    except ApiError as exc:
        detail = exc.body.get("detail") if isinstance(exc.body, dict) else str(exc.body or "")
        st.session_state[SIDEBAR_SAVED_SEARCHES_ERROR_KEY] = detail or "Failed to save search"
        st.rerun()
    except Exception:
        st.session_state[SIDEBAR_SAVED_SEARCHES_ERROR_KEY] = "Failed to save search"
        st.rerun()


def render_sidebar_saved_searches(cfg: ApiConfig, *, navigate_home_on_load: bool = False) -> None:
    user_id = _current_user_id()
    if user_id is None:
        return

    with st.sidebar:
        st.markdown("### Saved searches")

        info_message = st.session_state.pop(SIDEBAR_SAVED_SEARCHES_INFO_KEY, None)
        if info_message:
            st.success(info_message)

        error_message = st.session_state.pop(SIDEBAR_SAVED_SEARCHES_ERROR_KEY, None)
        if error_message:
            st.error(error_message)

        try:
            with ApiClient(cfg) as client:
                searches = client.users.list_saved_searches(user_id=user_id, limit=10)
        except ApiError as exc:
            detail = exc.body.get("detail") if isinstance(exc.body, dict) else str(exc.body or "")
            st.caption(detail or "Unable to load saved searches")
            return
        except Exception:
            st.caption("Unable to load saved searches")
            return

        if not searches:
            st.caption("No saved searches yet.")
            return

        st.table(
            [
                {
                    "Saved": _format_saved_time(s.created_at),
                    "Problem": ((s.problem_text or "").strip()[:32] or "-"),
                }
                for s in searches
            ]
        )

        options = {_saved_search_label(s): s for s in searches}
        selected_label = st.selectbox(
            "Select saved search",
            options=list(options.keys()),
            key=SIDEBAR_SAVED_SEARCHES_LOAD_SELECT_KEY,
            label_visibility="collapsed",
        )

        if st.button("Load selected", key="sidebar_load_saved_search", use_container_width=True):
            selected = options[selected_label]
            _apply_saved_search_to_home_form(selected)
            if navigate_home_on_load:
                st.switch_page("home_page.py")
                st.stop()
            st.rerun()
