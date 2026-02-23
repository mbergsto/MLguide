PREFIX mla:  <http://example.com/ml-articles/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

DELETE {
  mla:Cluster9 rdfs:label "defect, quality, inspection, machining"@en .
}
INSERT {
  mla:Cluster9 rdfs:label "process, manufacturing, defect, quality, inspection, machining"@en .
}
WHERE {
  mla:Cluster9 rdfs:label "defect, quality, inspection, machining"@en .
}