from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    graphdb_base_url: str = "http://127.0.0.1:7200"
    graphdb_repo_id: str = "ML-Ontology"
    database_url: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",   # Ignore extra fields in the .env file
    )

settings = Settings()