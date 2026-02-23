from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    backend_url: str = "http://localhost:8000"
    timeout_seconds: float = 30.0
    meta_cache_ttl_seconds: int = 3600
    max_results_default: int = 10

    # GitHub API setting, have to be moved to backend later
    github_token: str | None = None
    notebooks_repo_name: str = "mbergsto/generated-notebooks-mlguide"
    notebooks_repo_branch: str = "main"

    model_config = SettingsConfigDict(
        env_file="../.env",  
        extra="ignore"
    )

settings = Settings()