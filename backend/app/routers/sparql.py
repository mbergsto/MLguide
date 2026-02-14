# debug tool for testing GraphDB connectivity and executing SPARQL queries/updates

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient

router = APIRouter()

class SparqlQuery(BaseModel):
    query: str

class SparqlUpdate(BaseModel):
    update: str

@router.get("/health")
def health(db: GraphDBClient = Depends(get_graphdb)):
    try:
        db.select("SELECT (1 as ?ok) WHERE {}")
        return {"ok": True, "graphdb_reachable": True}
    except Exception as e:
        return {"ok": False, "graphdb_reachable": False, "error": str(e)}

@router.post("/select")
def sparql_select(payload: SparqlQuery, db: GraphDBClient = Depends(get_graphdb)):
    try:
        return db.select(payload.query)
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update")
def sparql_update(payload: SparqlUpdate, db: GraphDBClient = Depends(get_graphdb)):
    try:
        db.update(payload.update)
        return {"ok": True}
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
