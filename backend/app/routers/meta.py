import requests
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient
from app.services.sparql_templates import PREFIXES

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
    return run_select(db, q)

@router.get("/clusters")
def clusters(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:ApplicationCluster ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return run_select(db, q)

@router.get("/paradigms")
def paradigms(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:LearningParadigm ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return run_select(db, q)

@router.get("/tasks")
def tasks(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a :ML_task ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return run_select(db, q)

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
    return run_select(db, q)

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
    return run_select(db, q)

@router.get("/enums/performance")
def performance(db: GraphDBClient = Depends(get_graphdb)):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      ?a :performance ?iri .
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return run_select(db, q)
