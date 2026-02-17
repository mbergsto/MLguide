from __future__ import annotations

import base64
from datetime import datetime, timezone

import httpx


def upload_notebook_and_get_colab_url(
    notebook_json: str,
    method_key: str,
    token: str | None,
    repo_name: str,
    branch: str,
) -> str:
    if not token or not repo_name:
        raise RuntimeError("Missing GITHUB_TOKEN or NOTEBOOKS_REPO_NAME.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = f"notebooks/{method_key or 'method'}_{timestamp}.ipynb"
    api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"

    payload = {
        "message": f"Add generated notebook for {method_key or 'method'}",
        "content": base64.b64encode(notebook_json.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    res = httpx.put(api_url, headers=headers, json=payload, timeout=30.0)
    if res.is_error:
        detail = res.text[:400] if res.text else f"status={res.status_code}"
        raise RuntimeError(f"GitHub upload failed: {detail}")

    return f"https://colab.research.google.com/github/{repo_name}/blob/{branch}/{file_path}"
