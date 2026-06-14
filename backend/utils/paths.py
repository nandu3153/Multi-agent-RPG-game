"""Resolve data directory paths regardless of working directory."""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


def resolve_data_path(env_var: str, default_relative: str) -> Path:
    """Resolve LORE_DIR, STATE_DIR, etc. from env or sensible defaults."""
    raw = os.environ.get(env_var)
    if raw:
        path = Path(raw)
        if path.is_absolute():
            return path
        candidates = [
            PROJECT_ROOT / raw,
            BACKEND_DIR / raw,
            PROJECT_ROOT / raw.lstrip("./"),
            BACKEND_DIR / raw.replace("./backend/", "").replace("backend/", ""),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return (BACKEND_DIR / raw.replace("./backend/", "").replace("backend/", "")).resolve()
    return (BACKEND_DIR / default_relative).resolve()
