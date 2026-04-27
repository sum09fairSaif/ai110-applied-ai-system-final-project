from src.streamlit_app import build_user_preferences, recommendations_to_dataframe


def test_build_user_preferences_returns_expected_recommender_shape():
    """Check that Streamlit widget values become a valid recommender input dictionary."""
    prefs = build_user_preferences(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
        scoring_mode="genre_first",
        preferred_decade=2010,
        target_popularity=78,
        prefers_instrumental=None,
    )

    assert prefs["favorite_genre"] == "pop"
    assert prefs["favorite_mood"] == "happy"
    assert prefs["target_energy"] == 0.8
    assert prefs["scoring_mode"] == "genre_first"
    assert prefs["preferred_decade"] == 2010


def test_recommendations_to_dataframe_includes_ui_columns():
    """Check that recommendation diagnostics are converted into a display-ready table."""
    frame = recommendations_to_dataframe(
        [
            {
                "song": {
                    "title": "Test Song",
                    "artist": "Test Artist",
                    "genre": "pop",
                    "mood": "happy",
                },
                "score": 4.2,
                "confidence": 0.64,
                "warnings": ["Low-confidence recommendation: example warning"],
                "critique_notes": ["Self-critique: example note"],
                "explanation": "mode=balanced, genre match (+1.0)",
            }
        ]
    )

    assert list(frame.columns) == [
        "Rank",
        "Title",
        "Artist",
        "Genre",
        "Mood",
        "Score",
        "Confidence",
        "Warnings",
        "Critique",
    ]
    assert frame.iloc[0]["Title"] == "Test Song"
