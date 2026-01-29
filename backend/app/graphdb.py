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

    def select(self, sparql: str) -> Dict[str, Any]:
        r = requests.get(
            self.query_url,
            params={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            auth=self.auth,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def update(self, sparql_update: str) -> None:
        r = requests.post(
            self.update_url,
            data=sparql_update.encode("utf-8"),
            headers={"Content-Type": "application/sparql-update"},
            auth=self.auth,
            timeout=self.timeout,
        )
        r.raise_for_status()
