from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import sparql, meta, recommendations, users

app = FastAPI(title="GraphDB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sparql.router, prefix="/sparql", tags=["sparql"])
app.include_router(meta.router, prefix="/meta", tags=["meta"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(users.router, prefix="/users", tags=["users"])
