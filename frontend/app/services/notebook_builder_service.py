from __future__ import annotations

from typing import Any

import jupytext
import nbformat


def _set_notebook_metadata(notebook: Any, method_title: str) -> None:
    notebook.metadata["colab"] = {"name": f"{method_title}.ipynb"}
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata["language_info"] = {"name": "python"}


def build_notebook_json(method_title: str, notebook_source: str) -> str:
    notebook = jupytext.reads(f"{notebook_source.rstrip()}\n", fmt="py:percent")
    _set_notebook_metadata(notebook, method_title)
    return nbformat.writes(notebook, version=4)
