"""Evaluation harness for recommendation reliability metrics."""

from __future__ import annotations

import os
import sys
from statistics import mean

sys.path.insert(0, os.path.dirname(__file__))

from profiles import USER_PROFILES
from recommender import load_songs, recommend_songs_with_diagnostics


def _average(values: list[float]) -> float:
    """Return a safe average for a numeric list."""
    return mean(values) if values else 0.0


def _calculate_genre_diversity(recommendations: list[dict]) -> float:
    """Measure how many unique genres appear in the recommendation list."""
    if not recommendations:
        return 0.0
    unique_genres = {item["song"]["genre"] for item in recommendations}
    return len(unique_genres) / len(recommendations)


def evaluate_profile(profile_name: str, user_prefs: dict, songs: list[dict], k: int = 5) -> dict:
    """Run one evaluation profile and compute summary metrics."""
    recommendations = recommend_songs_with_diagnostics(user_prefs, songs, k=k)
    confidences = [item["confidence"] for item in recommendations]
    warning_count = sum(len(item["warnings"]) for item in recommendations)
    low_confidence_count = sum(
        1 for item in recommendations
        if any("Low-confidence recommendation" in warning for warning in item["warnings"])
    )
    exact_match_count = sum(
        1 for item in recommendations
        if "genre match" in item["explanation"] or "mood match" in item["explanation"]
    )

    return {
        "profile_name": profile_name,
        "scoring_mode": user_prefs.get("scoring_mode", "balanced"),
        "result_count": len(recommendations),
        "average_confidence": _average(confidences),
        "low_confidence_count": low_confidence_count,
        "low_confidence_rate": low_confidence_count / len(recommendations) if recommendations else 0.0,
        "warning_count": warning_count,
        "warning_rate": warning_count / len(recommendations) if recommendations else 0.0,
        "genre_diversity": _calculate_genre_diversity(recommendations),
        "exact_match_rate": exact_match_count / len(recommendations) if recommendations else 0.0,
        "top_recommendation": recommendations[0]["song"]["title"] if recommendations else "None",
    }


def evaluate_profiles(
    profiles: dict[str, dict],
    songs: list[dict],
    k: int = 5,
) -> list[dict]:
    """Evaluate a collection of profiles and return one report row per profile."""
    return [
        evaluate_profile(profile_name, user_prefs, songs, k=k)
        for profile_name, user_prefs in profiles.items()
    ]


def summarize_evaluation(results: list[dict]) -> dict:
    """Aggregate profile-level evaluation results into one summary block."""
    if not results:
        return {
            "profiles_evaluated": 0,
            "average_confidence": 0.0,
            "average_low_confidence_rate": 0.0,
            "average_warning_rate": 0.0,
            "average_genre_diversity": 0.0,
            "average_exact_match_rate": 0.0,
            "strongest_profile": "None",
            "weakest_profile": "None",
        }

    return {
        "profiles_evaluated": len(results),
        "average_confidence": _average([item["average_confidence"] for item in results]),
        "average_low_confidence_rate": _average([item["low_confidence_rate"] for item in results]),
        "average_warning_rate": _average([item["warning_rate"] for item in results]),
        "average_genre_diversity": _average([item["genre_diversity"] for item in results]),
        "average_exact_match_rate": _average([item["exact_match_rate"] for item in results]),
        "strongest_profile": max(results, key=lambda item: item["average_confidence"])["profile_name"],
        "weakest_profile": min(results, key=lambda item: item["average_confidence"])["profile_name"],
    }


def format_evaluation_report(results: list[dict], summary: dict) -> str:
    """Render a concise plain-text evaluation report."""
    lines = ["Evaluation Summary"]
    lines.append(f"Profiles evaluated: {summary['profiles_evaluated']}")
    lines.append(f"Average confidence: {summary['average_confidence']:.2f}")
    lines.append(f"Average low-confidence rate: {summary['average_low_confidence_rate']:.2f}")
    lines.append(f"Average warning rate: {summary['average_warning_rate']:.2f}")
    lines.append(f"Average genre diversity: {summary['average_genre_diversity']:.2f}")
    lines.append(f"Average exact-match rate: {summary['average_exact_match_rate']:.2f}")
    lines.append(f"Strongest profile: {summary['strongest_profile']}")
    lines.append(f"Weakest profile: {summary['weakest_profile']}")
    lines.append("")
    lines.append("Per-profile results")

    for result in results:
        lines.append(
            f"- {result['profile_name']}: avg_conf={result['average_confidence']:.2f}, "
            f"low_conf_rate={result['low_confidence_rate']:.2f}, "
            f"genre_diversity={result['genre_diversity']:.2f}, "
            f"top={result['top_recommendation']}"
        )

    return "\n".join(lines)


def main() -> None:
    """Run the evaluation harness from the command line."""
    songs = load_songs("data/songs.csv")
    results = evaluate_profiles(USER_PROFILES, songs, k=5)
    summary = summarize_evaluation(results)
    print(format_evaluation_report(results, summary))


if __name__ == "__main__":
    main()
