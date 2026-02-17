from __future__ import annotations

from pathlib import Path

import streamlit as st

from api import ApiError
from models import ArticleItem
from utils import build_doi_url


def render_missing_navigation_state() -> None:
    st.title("Method details")
    st.info("Failed to load method details. Go back to recommendations.")


def render_page_title(method_title: str) -> None:
    st.title(f"Method details: {method_title}")


def render_template_section(rendered_code: str, template_method: str) -> None:
    st.subheader("Generated scikit-learn template")
    st.caption(f"Template method key: `{template_method or 'unknown'}`")
    st.code(rendered_code, language="python")
    st.download_button(
        label="Download generated template (.py)",
        data=rendered_code,
        file_name=f"{template_method or 'method'}_template.py",
        mime="text/x-python",
    )


def render_colab_button(has_colab_cfg: bool) -> bool:
    return st.button("Open in Colab", type="primary", disabled=not has_colab_cfg)


def render_colab_config_hint() -> None:
    st.caption("Set `GITHUB_TOKEN` and `NOTEBOOKS_REPO_NAME` to enable Colab export.")


def render_colab_link(colab_url: str) -> None:
    st.link_button("Launch in Colab", colab_url)


def render_colab_error(error: Exception) -> None:
    st.error(f"Could not create Colab link: {error}")


def render_template_not_found(template_path: Path) -> None:
    st.warning(f"Template file not found: {template_path}")


def render_supporting_articles(articles: list[ArticleItem]) -> None:
    st.subheader("Supporting articles")
    if not articles:
        st.write("-")
        return

    for article in articles:
        title = article.label or "Untitled article"
        doi_url = build_doi_url(article.doi)
        st.markdown(f"- **{title}** - [{article.doi}]({doi_url})")


def render_api_error(error: ApiError) -> None:
    st.error(f"{error} ({error.status})")
