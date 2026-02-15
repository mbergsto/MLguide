import streamlit as st
from api import ApiClient, ApiConfig, ApiError
from models import RecommendationRequest

st.set_page_config(page_title="Method details", layout="wide")

cfg = ApiConfig()

# read from query params first
approach_iri = st.query_params.get("approach_iri")

# fallback to session_state if you still want it
if not approach_iri:
    approach_iri = st.session_state.get("selected_approach_iri")

payload = st.session_state.get("last_request_payload")

st.title("Method details")

if not approach_iri or not payload:
    st.info("No method selected. Go back to recommendations.")
    st.stop()

req = RecommendationRequest.model_validate(payload)

try:
    with ApiClient(cfg) as client:
        details = client.recommendations.details(req, approach_iri)
    st.write(details.model_dump())
except ApiError as e:
    st.error(f"{e} ({e.status})")
    st.stop()
