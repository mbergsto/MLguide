from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from app.settings import settings
from app.graphdb import GraphDBClient

app = FastAPI(title="GraphDB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = GraphDBClient(
    base_url=settings.graphdb_base_url,
    repo_id=settings.graphdb_repo_id,
)

class SparqlQuery(BaseModel):
    query: str

class SparqlUpdate(BaseModel):
    update: str

@app.get("/health")
def health():
    try:
        db.select("SELECT (1 as ?ok) WHERE {}")
        return {"ok": True, "graphdb_reachable": True}
    except Exception as e:
        return {"ok": False, "graphdb_reachable": False, "error": str(e)}


@app.post("/sparql/select")
def sparql_select(payload: SparqlQuery):
    try:
        return db.select(payload.query)
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sparql/update")
def sparql_update(payload: SparqlUpdate):
    try:
        db.update(payload.update)
        return {"ok": True}
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

