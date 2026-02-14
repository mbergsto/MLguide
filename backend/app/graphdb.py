import requests
from typing import Any, Dict, Optional

class GraphDBClient:
    def __init__(
        self,
        base_url: str,
        repo_id: str,
        auth: Optional[tuple[str, str]] = None,
        timeout: int = 30,
    ):
        self.query_url = f"{base_url}/repositories/{repo_id}"
        self.update_url = f"{base_url}/repositories/{repo_id}/statements"
        self.auth = auth
        self.timeout = timeout
        self.session = requests.Session()  # Use a session for connection pooling
        
    def close(self):
        self.session.close()

    def select(self, sparql: str) -> Dict[str, Any]:
        r = self.session.post(  # Post and not Get, because some queries might be too long for URL parameters, and with Post the data is sent in the body.
            url=self.query_url,
            data={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            auth=self.auth,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def update(self, sparql_update: str) -> None:
        r = self.session.post(
            self.update_url,
            data=sparql_update.encode("utf-8"),
            headers={"Content-Type": "application/sparql-update"},
            auth=self.auth,
            timeout=self.timeout,
        )
        r.raise_for_status()
        

