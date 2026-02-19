# MLguide

Streamlit + FastAPI + GraphDB application for thesis work (related work found in ML-catalogue repo)

This project consists of:

- **Backend:** FastAPI API that communicates with a GraphDB repository via SPARQL
- **Frontend:** Streamlit UI for running recommendation workflows

---

## Requirements

- Python 3.10+
- A running GraphDB instance
- Docker + Docker Compose (recommended for deployment)

---

## Backend Setup

### 1. Install Python dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure GraphDB connection (optional)

Edit `backend/app/settings.py` if needed:

```python
graphdb_base_url = "http://127.0.0.1:7200"
graphdb_repo_id  = "ML-Ontology"
```

### 3. Start the API

```bash
uvicorn main:app --reload --port 8000
```

Backend is now running at: [http://localhost:8000](http://localhost:8000)

Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start development server

```bash
streamlit run app/home_page.py
```

Frontend is now running at: [http://localhost:8501](http://localhost:8501)

---
