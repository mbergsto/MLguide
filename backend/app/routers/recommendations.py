import requests
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient
from app.services.recommendation_service import RecommendationRequest, build_recommendation_query
from app.services.sparql_results import bindings_to_rows

router = APIRouter()

@router.post("")
def recommend(req: RecommendationRequest, db: GraphDBClient = Depends(get_graphdb)):
    """
    Generate recommendations based on the provided request.
    
    Args:
        req: The recommendation request containing query parameters.
        db: The GraphDB client dependency for database access.
    
    Returns:
        A list of rows containing recommendation results.
    
    Raises:
        HTTPException: 502 if GraphDB returns an HTTP error, 500 for other errors.
    """
    sparql = build_recommendation_query(req)
    try:
        raw = db.select(sparql)
        rows = bindings_to_rows(raw)
        return rows
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
