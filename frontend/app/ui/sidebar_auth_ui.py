from __future__ import annotations

import streamlit as st

from integrations.api import ApiConfig, ApiClient, ApiError


AUTH_USER_KEY = "auth_user"
AUTH_ERROR_KEY = "auth_error"


def render_sidebar_auth(cfg: ApiConfig) -> None:
    user = st.session_state.get(AUTH_USER_KEY)

    with st.sidebar:
        st.markdown("### User" if user else "### Log in")

        if user:
            username = user.get("username", "")
            st.markdown(f"👤 **{username}**")
            if st.button("Log out", key="sidebar_logout", use_container_width=True):
                st.session_state.pop(AUTH_USER_KEY, None)
                st.session_state.pop(AUTH_ERROR_KEY, None)
                st.rerun()
            return

        error_message = st.session_state.pop(AUTH_ERROR_KEY, None)
        if error_message:
            st.error(error_message)

        with st.form("sidebar_login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                key="sidebar_login_username",
                placeholder="Enter username",
            )
            submitted = st.form_submit_button("Log in", use_container_width=True)

        if not submitted:
            return

        clean_username = (username or "").strip()
        if not clean_username:
            st.session_state[AUTH_ERROR_KEY] = "Please enter a username."
            st.rerun()
        if len(clean_username) < 4:
            st.session_state[AUTH_ERROR_KEY] = "Username must be at least 4 characters."
            st.rerun()

        try:
            with ApiClient(cfg) as client:
                logged_in_user = client.users.login(clean_username)
            st.session_state[AUTH_USER_KEY] = logged_in_user.model_dump()
            st.rerun()
        except ApiError as exc:
            detail = exc.body.get("detail") if isinstance(exc.body, dict) else str(exc.body or "")
            st.session_state[AUTH_ERROR_KEY] = detail or "Login failed"
            st.rerun()
        except Exception:
            st.session_state[AUTH_ERROR_KEY] = "Login failed"
            st.rerun()
