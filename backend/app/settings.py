from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    graphdb_base_url: str = "http://127.0.0.1:7200"
    graphdb_repo_id: str = "ML-Ontology"

settings = Settings()
