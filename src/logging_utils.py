"""Logging helpers for recommendation runs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


DEFAULT_LOG_PATH = Path("logs") / "recommendation_log.jsonl"


def build_recommendation_log_entry(
    profile_name: str,
    user_prefs: dict,
    recommendations: list[dict],
) -> dict:
    """Create a structured log entry for one recommendation run."""
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "profile_name": profile_name,
        "user_preferences": user_prefs,
        "scoring_mode": user_prefs.get("scoring_mode", "balanced"),
        "result_count": len(recommendations),
        "recommendations": recommendations,
        "warning_count": sum(len(result.get("warnings", [])) for result in recommendations),
    }


def append_jsonl_log(entry: dict, log_path: Path | str = DEFAULT_LOG_PATH) -> Path:
    """Append one JSON object to a JSONL log file and return the resolved path."""
    destination = Path(log_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=True) + "\n")

    return destination.resolve()
