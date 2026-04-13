from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = REPO_ROOT / "runs"
SCHEMA_CACHE_DIR = REPO_ROOT / "schema_cache"
PATTERN_CACHE_DIR = REPO_ROOT / "pattern_cache"


def load_env(env_file: Path | None = None) -> None:
    """Load a local .env file without adding a dependency on python-dotenv."""
    env_path = env_file or REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def episode_dir(name: str) -> Path:
    path = RUNS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")


def raw_markdown(markdown: Any) -> str:
    if hasattr(markdown, "raw_markdown"):
        return markdown.raw_markdown or ""
    return str(markdown or "")


def fit_markdown(markdown: Any) -> str:
    if hasattr(markdown, "fit_markdown"):
        return markdown.fit_markdown or ""
    return ""


def preview(text: str, size: int = 200) -> str:
    return text[:size].replace("\n", " ").strip()

