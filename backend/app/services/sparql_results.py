from typing import Any, Dict, List


def parse_value(binding: Dict[str, Any]) -> Any:
    """Convert a SPARQL binding value into a plain Python value."""
    value = binding.get("value")
    datatype = binding.get("datatype")

    if value is None:
        return None

    if datatype:
        if datatype.endswith("integer") or datatype.endswith("int") or datatype.endswith("long"):
            try:
                return int(value)
            except ValueError:
                return value

        if datatype.endswith("decimal") or datatype.endswith("double") or datatype.endswith("float"):
            try:
                return float(value)
            except ValueError:
                return value

        if datatype.endswith("boolean"):
            return value.lower() == "true"

    return value


def bindings_to_rows(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transform SPARQL JSON bindings into a list of plain dictionaries."""
    bindings = raw.get("results", {}).get("bindings", [])
    rows: List[Dict[str, Any]] = []

    for b in bindings:
        row: Dict[str, Any] = {}
        for key, val in b.items():
            row[key] = parse_value(val)
        rows.append(row)

    return rows


def rows_to_options(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert rows into [{iri, label}] option objects for UI use."""
    options: List[Dict[str, str]] = []

    for r in rows:
        iri = r.get("iri")
        label = r.get("label")

        if isinstance(iri, str) and isinstance(label, str):
            options.append({"iri": iri, "label": label})

    return options
