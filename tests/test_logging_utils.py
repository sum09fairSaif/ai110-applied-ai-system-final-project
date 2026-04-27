import json
from pathlib import Path

from src.logging_utils import append_jsonl_log, build_recommendation_log_entry


def test_build_recommendation_log_entry_includes_core_fields():
    """Check that a recommendation log entry captures the main evaluation details."""
    recommendations = [
        {
            "song": {"title": "Test Song", "artist": "Test Artist"},
            "score": 4.2,
            "confidence": 0.64,
            "explanation": "mode=balanced, mood match (+1.0)",
            "warnings": ["No exact genre or mood match was found, so this recommendation depends on secondary signals."],
        }
    ]

    entry = build_recommendation_log_entry(
        "Test Profile",
        {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
            "scoring_mode": "balanced",
        },
        recommendations,
    )

    assert entry["profile_name"] == "Test Profile"
    assert entry["scoring_mode"] == "balanced"
    assert entry["result_count"] == 1
    assert entry["warning_count"] == 1
    assert "timestamp_utc" in entry


def test_append_jsonl_log_writes_one_json_object_per_line():
    """Check that recommendation log entries are appended as JSONL records."""
    log_dir = Path("tests") / "_tmp_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "recommendation_log.jsonl"
    entry = {
        "profile_name": "Test Profile",
        "scoring_mode": "balanced",
        "recommendations": [],
        "warning_count": 0,
    }

    try:
        written_path = append_jsonl_log(entry, log_path=log_path)

        assert written_path == log_path.resolve()
        log_lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(log_lines) == 1
        assert json.loads(log_lines[0])["profile_name"] == "Test Profile"
    finally:
        if log_path.exists():
            log_path.unlink()
        if log_dir.exists():
            log_dir.rmdir()
