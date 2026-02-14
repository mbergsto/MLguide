import requests
from requests.exceptions import Timeout, ReadTimeout
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient
from app.services.recommendation_service import (
    RecommendationRequest,
    RecommendationDetailsRequest,
    build_recommendation_query,
    build_details_articles_query,
    build_details_matches_query,
)
from app.services.sparql_results import bindings_to_rows

import time, uuid
import logging
logger = logging.getLogger("uvicorn.error") 

router = APIRouter()


@router.post("")
def recommend(req: RecommendationRequest, db: GraphDBClient = Depends(get_graphdb)):
    sparql = build_recommendation_query(req)
    try:
        raw = db.select(sparql)
        return bindings_to_rows(raw)
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/details")
def details(req: RecommendationDetailsRequest, db: GraphDBClient = Depends(get_graphdb)):
    rid = str(uuid.uuid4())[:8]
    try:
        logger.info("details rid=%s running articles query", rid)
        raw_articles = db.select(build_details_articles_query(req))
        logger.info("details rid=%s running matches query", rid)

        raw_matches = None
        if req.conditions or req.performance_prefs or req.task_iri:
            raw_matches = db.select(build_details_matches_query(req))
        else:
            raw_matches = {"results": {"bindings": []}}  # empty matches if no conditions/performance/task prefs
            
        articles = bindings_to_rows(raw_articles)
        matches_rows = bindings_to_rows(raw_matches)

        conditions = {}
        performance = {}
        tasks = {}

        for r in matches_rows:
            if r.get("cond"):
                conditions[r["cond"]] = r.get("condLabel") or r["cond"]
            if r.get("perf"):
                performance[r["perf"]] = r.get("perfLabel") or r["perf"]
            if r.get("task"):
                tasks[r["task"]] = r.get("taskLabel") or r["task"]

        return {
            "approachIri": req.approach_iri,
            "articles": [
                {"article": a.get("article"), "doi": a.get("doi"), "label": a.get("label")}
                for a in articles
                if a.get("doi")
            ],
            "matches": {
                "conditions": [{"iri": iri, "label": label} for iri, label in conditions.items()],
                "performance": [{"iri": iri, "label": label} for iri, label in performance.items()],
                "tasks": [{"iri": iri, "label": label} for iri, label in tasks.items()],
            },
        }
    except (Timeout, ReadTimeout):
        logger.exception("GraphDB timeout in /details rid=%s", rid)
        raise HTTPException(status_code=504, detail="GraphDB query timed out")

    except requests.HTTPError as e:
        logger.exception("GraphDB HTTPError in /details rid=%s", rid)
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")

    except Exception as e:
        logger.exception("Unhandled error in /details rid=%s", rid)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


