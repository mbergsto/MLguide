from __future__ import annotations

from pathlib import Path

import streamlit as st

from api import ApiError
from models import ArticleItem
from utils import build_doi_url


def _clear_article_search() -> None:
    st.session_state["details_article_search"] = ""


def render_missing_navigation_state() -> None:
    st.title("MLguide 🤖")
    st.info("Failed to load method details. Go back to recommendations.")


def render_page_title(method_title: str) -> None:
    st.title(method_title)


def render_notebook_preview(rendered_code: str) -> None:
    st.subheader("Generated ML notebook")
    with st.container(height=520, border=True):
        st.code(rendered_code, language="python")


def render_template_actions(
    template_method: str,
    notebook_json: str,
    has_colab_cfg: bool,
) -> bool:
    c1, c2 = st.columns([1.1, 1.0], gap="small", vertical_alignment="center")
    with c1:
        st.download_button(
            label="Download notebook (.ipynb)",
            data=notebook_json,
            file_name=f"{template_method or 'method'}_template.ipynb",
            mime="application/x-ipynb+json",
            use_container_width=True,
        )
    with c2:
        return st.button(
            "Open in Colab",
            type="primary",
            disabled=not has_colab_cfg,
            use_container_width=True,
        )


def render_context_panel(items: list[tuple[str, str]]) -> None:
    st.subheader("")
    with st.container(border=True):
        if not items:
            st.write("-")
            return
        for label, value in items:
            st.markdown(f"**{label}:** {value}")


def render_colab_config_hint() -> None:
    st.caption("Set `GITHUB_TOKEN` and `NOTEBOOKS_REPO_NAME` to enable Colab export.")


def render_colab_error(error: Exception) -> None:
    st.error(f"Could not create Colab link: {error}")


def render_template_not_found(template_path: Path) -> None:
    st.warning(f"Template file not found: {template_path}")


def render_supporting_articles(articles: list[ArticleItem]) -> None:
    st.subheader("Supporting articles")
    search_key = "details_article_search"
    c1, c2 = st.columns([4.0, 1.0], gap="small", vertical_alignment="bottom")
    with c1:
        query = st.text_input(
            "Search articles",
            value="",
            placeholder="Search by title or DOI",
            key=search_key,
        ).strip().lower()
    with c2:
        st.button(
            "Clear",
            key="details_article_search_clear",
            use_container_width=True,
            on_click=_clear_article_search,
        )

    filtered_articles = [
        article
        for article in articles
        if not query
        or query in (article.label or "").lower()
        or query in (article.doi or "").lower()
    ]

    with st.container(height=360, border=True):
        if not filtered_articles:
            st.write("-")
            return

        for article in filtered_articles:
            title = article.label or "Untitled article"
            doi_url = build_doi_url(article.doi)
            st.markdown(f"- **{title}** - [{article.doi}]({doi_url})")


def render_api_error(error: ApiError) -> None:
    st.error(f"{error} ({error.status})")
