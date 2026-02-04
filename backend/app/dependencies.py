from app.settings import settings
from app.graphdb import GraphDBClient

def get_graphdb() -> GraphDBClient:
    return GraphDBClient(
        base_url=settings.graphdb_base_url,
        repo_id=settings.graphdb_repo_id,
    )
