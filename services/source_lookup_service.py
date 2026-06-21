"""Source lookup helpers used by compliance workflow rendering."""

from __future__ import annotations

from typing import Any


def source_by_id(source_chunks: list[dict[str, Any]] | None, source_id: str | None) -> dict[str, Any]:
    """Return the first source chunk matching a source id.

    Returns an empty dictionary when no source is found. This keeps UI code
    simple and avoids direct dependency on local helper functions.
    """

    if not source_chunks or not source_id:
        return {}

    for chunk in source_chunks:
        if str(chunk.get("source_id", "")).strip() == str(source_id).strip():
            return chunk

    return {}
