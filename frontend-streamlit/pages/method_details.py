import streamlit as st
from api import ApiClient, ApiConfig, ApiError
from models import RecommendationRequest

st.set_page_config(page_title="Method details", layout="wide")

cfg = ApiConfig()

# Read navigation state
approach_iri = st.query_params.get("approach_iri")
payload = st.session_state.get("last_request_payload")

st.title("Method details")

# Missing navigation state
if not approach_iri or not payload:
    st.info("Failed to load method details. Go back to recommendations.")
    st.stop()

# Rebuild request from stored payload
req = RecommendationRequest.model_validate(payload)

try:
    # Fetch details from backend
    with ApiClient(cfg) as client:
        details = client.recommendations.details(req, approach_iri)

    st.subheader("Supporting articles")

    # Empty state
    if not details.articles:
        st.write("—")
        st.stop()

    # Render article list with clickable DOI links
    for a in details.articles:
        title = a.label or "Untitled article"
        doi_url = f"https://doi.org/{a.doi}"
        st.markdown(f"- **{title}** — [{a.doi}]({doi_url})")

except ApiError as e:
    st.error(f"{e} ({e.status})")
    st.stop()
