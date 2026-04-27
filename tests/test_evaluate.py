from src.evaluate import evaluate_profile, format_evaluation_report, summarize_evaluation


def test_evaluate_profile_returns_expected_metric_fields():
    """Check that one profile evaluation returns the core reliability metrics."""
    songs = [
        {
            "id": 1,
            "title": "Exact Match",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120.0,
            "valence": 0.7,
            "danceability": 0.7,
            "acousticness": 0.2,
        },
        {
            "id": 2,
            "title": "Mismatch",
            "artist": "Artist B",
            "genre": "ambient",
            "mood": "peaceful",
            "energy": 0.3,
            "tempo_bpm": 70.0,
            "valence": 0.5,
            "danceability": 0.3,
            "acousticness": 0.9,
        },
    ]

    result = evaluate_profile(
        "Test Profile",
        {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
            "scoring_mode": "balanced",
        },
        songs,
        k=2,
    )

    assert result["profile_name"] == "Test Profile"
    assert result["result_count"] == 2
    assert 0.0 <= result["average_confidence"] <= 1.0
    assert 0.0 <= result["genre_diversity"] <= 1.0
    assert result["top_recommendation"] == "Exact Match"


def test_summarize_evaluation_identifies_strongest_and_weakest_profiles():
    """Check that aggregate evaluation picks out the highest- and lowest-confidence profiles."""
    summary = summarize_evaluation(
        [
            {
                "profile_name": "Strong Profile",
                "average_confidence": 0.8,
                "low_confidence_rate": 0.1,
                "warning_rate": 0.2,
                "genre_diversity": 0.6,
                "exact_match_rate": 0.8,
            },
            {
                "profile_name": "Weak Profile",
                "average_confidence": 0.4,
                "low_confidence_rate": 0.6,
                "warning_rate": 0.7,
                "genre_diversity": 0.5,
                "exact_match_rate": 0.2,
            },
        ]
    )

    assert summary["profiles_evaluated"] == 2
    assert summary["strongest_profile"] == "Strong Profile"
    assert summary["weakest_profile"] == "Weak Profile"


def test_format_evaluation_report_contains_summary_and_profile_rows():
    """Check that the report formatter prints both aggregate and per-profile information."""
    report = format_evaluation_report(
        [
            {
                "profile_name": "Test Profile",
                "average_confidence": 0.65,
                "low_confidence_rate": 0.20,
                "genre_diversity": 0.60,
                "top_recommendation": "Exact Match",
            }
        ],
        {
            "profiles_evaluated": 1,
            "average_confidence": 0.65,
            "average_low_confidence_rate": 0.20,
            "average_warning_rate": 0.30,
            "average_genre_diversity": 0.60,
            "average_exact_match_rate": 0.80,
            "strongest_profile": "Test Profile",
            "weakest_profile": "Test Profile",
        },
    )

    assert "Evaluation Summary" in report
    assert "Profiles evaluated: 1" in report
    assert "- Test Profile: avg_conf=0.65" in report
