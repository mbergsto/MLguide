from __future__ import annotations

import streamlit as st


def render_back_nav(key_prefix: str = "nav") -> bool:
    c1, _ = st.columns([0.9, 12.1], gap="small", vertical_alignment="center")
    with c1:
        back_clicked = st.button("Back", key=f"{key_prefix}_back", use_container_width=True)

    st.markdown("<hr style='margin: 0.1rem 0 0.35rem 0; border-color: #ddd;'>", unsafe_allow_html=True)
    return back_clicked
