from pydantic import BaseModel
import os

class Settings(BaseModel):
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "30.0"))
    meta_cache_ttl_seconds: int = int(os.getenv("META_CACHE_TTL_SECONDS", "3600"))
    max_results_default: int = int(os.getenv("MAX_RESULTS_DEFAULT", "10"))
    
settings = Settings()