from typing import List, Optional
from pydantic import BaseModel

from app.services.sparql_templates import PREFIXES

class RecommendationRequest(BaseModel):
    problem_text: Optional[str] = None
    phase_iri: str
    cluster_iri: str
    paradigm_iri: str
    task_iri: Optional[str] = None
    conditions: List[str] = []
    performance_prefs: List[str] = []

def build_recommendation_query(req: RecommendationRequest) -> str:
    not_possible = ""
    possible_if = ""
    performance = ""
    task = ""

    if req.conditions:
        cond_vals = " ".join(f"<{c}>" for c in req.conditions)
        not_possible = f"""
        FILTER NOT EXISTS {{
          ?approach :not_possible_if ?blockedCond .
          VALUES ?blockedCond {{ {cond_vals} }}
        }}
        """
        possible_if = f"""
        OPTIONAL {{
          ?approach :possible_if ?posMatch .
          VALUES ?posMatch {{ {cond_vals} }}
        }}
        """

    if req.performance_prefs:
        perf_vals = " ".join(f"<{p}>" for p in req.performance_prefs)
        performance = f"""
        OPTIONAL {{
          ?approach :performance ?perfMatch .
          VALUES ?perfMatch {{ {perf_vals} }}
        }}
        """

    if req.task_iri:
        task = f"""
        OPTIONAL {{
          ?approach :used_for ?taskMatch .
          FILTER(?taskMatch = <{req.task_iri}>)
        }}
        """

    return PREFIXES + f"""
    SELECT
      ?method ?methodLabel
      ?approach ?approachLabel
      (COUNT(DISTINCT ?article) AS ?supportingArticles)
      (COUNT(DISTINCT ?posMatch) AS ?possibleIfMatches)
      (COUNT(DISTINCT ?perfMatch) AS ?performanceMatches)
      (COUNT(DISTINCT ?taskMatch) AS ?taskMatches)
    WHERE {{
      VALUES (?phase ?cluster ?paradigm) {{
        (<{req.phase_iri}> <{req.cluster_iri}> <{req.paradigm_iri}>)
      }}

      ?article a mla:Article ;
              mla:hasPhase ?phase ;
              mla:hasCluster ?cluster ;
              mla:hasParadigm ?paradigm ;
              mla:mentionsMethod ?method .

      OPTIONAL {{ ?method rdfs:label ?methodLabel }}

      ?method skos:exactMatch ?approach .
      OPTIONAL {{ ?approach skos:prefLabel ?approachLabel }}

      {not_possible}
      {possible_if}
      {performance}
      {task}
    }}
    GROUP BY ?method ?methodLabel ?approach ?approachLabel
    ORDER BY
      DESC(?supportingArticles)
      DESC(?taskMatches)
      DESC(?possibleIfMatches)
      DESC(?performanceMatches)
    LIMIT 15
    """
