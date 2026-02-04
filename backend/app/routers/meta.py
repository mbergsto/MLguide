import requests
from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_graphdb
from app.graphdb import GraphDBClient
from app.services.sparql_templates import PREFIXES
from app.services.sparql_results import bindings_to_rows, rows_to_options

router = APIRouter()

def run_select(db: GraphDBClient, sparql: str):
    try:
        return db.select(sparql)
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GraphDB error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phases")
def phases(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:LifecyclePhase ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/clusters")
def clusters(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:ApplicationCluster ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/paradigms")
def paradigms(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:LearningParadigm ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/tasks")
def tasks(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a :ML_task ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/enums/dataset-types")
def dataset_types(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      ?task a :ML_task ;
            :has_dataset_type ?iri .
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/enums/conditions")
def conditions(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      { ?a :possible_if ?iri . }
      UNION
      { ?a :not_possible_if ?iri . }
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))

@router.get("/enums/performance")
def performance(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      ?a :performance ?iri .
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    raw = run_select(db, q)
    return rows_to_options(bindings_to_rows(raw))
