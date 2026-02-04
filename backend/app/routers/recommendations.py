import requests
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient
from app.services.recommendation_service import RecommendationRequest, build_recommendation_query

router = APIRouter()

@router.post("")
def recommend(req: RecommendationRequest, db: GraphDBClient = Depends(get_graphdb)):
    sparql = build_recommendation_query(req)
    try:
        return db.select(sparql)
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
