from __future__ import annotations

import streamlit as st


def render_navbar(show_back: bool = False, key_prefix: str = "nav") -> tuple[bool, bool]:
    c1, c2, c3 = st.columns([1, 1, 8])

    with c1:
        home_clicked = st.button("MLguide 🤖", key=f"{key_prefix}_home")

    back_clicked = False
    if show_back:
        with c2:
            back_clicked = st.button("Back", key=f"{key_prefix}_back")
    else:
        with c2:
            st.empty()

    st.divider()
    return home_clicked, back_clicked
