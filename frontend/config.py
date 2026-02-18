from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "30.0"))
    meta_cache_ttl_seconds: int = int(os.getenv("META_CACHE_TTL_SECONDS", "3600"))
    max_results_default: int = int(os.getenv("MAX_RESULTS_DEFAULT", "10"))
    github_token: str | None = os.getenv("GITHUB_TOKEN")
    notebooks_repo_name: str = os.getenv("NOTEBOOKS_REPO_NAME", "mbergsto/generated-notebooks-mlguide")
    notebooks_repo_branch: str = os.getenv("NOTEBOOKS_REPO_BRANCH", "main")
    
settings = Settings()
