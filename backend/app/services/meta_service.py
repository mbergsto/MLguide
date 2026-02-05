import requests
from fastapi import HTTPException

from app.graphdb import GraphDBClient
from app.services.sparql_templates import PREFIXES
from app.services.sparql_results import bindings_to_rows, rows_to_options


def _run_select(db: GraphDBClient, sparql: str):
    try:
        return db.select(sparql)
    except requests.HTTPError as e:
        detail = getattr(getattr(e, "response", None), "text", str(e))
        raise HTTPException(status_code=502, detail=f"GraphDB error: {detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _select_options(db: GraphDBClient, sparql: str):
    raw = _run_select(db, sparql)
    return rows_to_options(bindings_to_rows(raw))


def get_phases(db: GraphDBClient):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:LifecyclePhase ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_clusters(db: GraphDBClient):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:ApplicationCluster ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_paradigms(db: GraphDBClient):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a mla:LearningParadigm ;
           rdfs:label ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_tasks(db: GraphDBClient):
    q = PREFIXES + """
    SELECT ?iri ?label WHERE {
      ?iri a :ML_task ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_dataset_types(db: GraphDBClient):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      ?task a :ML_task ;
            :has_dataset_type ?iri .
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_conditions(db: GraphDBClient):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      { ?a :possible_if ?iri . }
      UNION
      { ?a :not_possible_if ?iri . }
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)


def get_performance(db: GraphDBClient):
    q = PREFIXES + """
    SELECT DISTINCT ?iri ?label WHERE {
      ?a :performance ?iri .
      ?iri a :Enum ;
           skos:prefLabel ?label .
    } ORDER BY LCASE(STR(?label))
    """
    return _select_options(db, q)
