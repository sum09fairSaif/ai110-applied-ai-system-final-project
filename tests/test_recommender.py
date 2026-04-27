import pytest

from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    recommend_songs,
    recommend_songs_with_diagnostics,
    score_song,
)

def make_small_recommender() -> Recommender:
    """Create a tiny two-song recommender that the tests can use quickly."""
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    """Check that the stronger match appears before the weaker one."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    """Check that the recommender gives a written explanation instead of a blank result."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_scoring_modes_can_change_ranking_priority():
    """Check that changing the scoring mode can change which song comes first."""
    songs = [
        Song(
            id=1,
            title="Exact Genre Song",
            artist="Test Artist",
            genre="pop",
            mood="sad",
            energy=0.4,
            tempo_bpm=100,
            valence=0.4,
            danceability=0.5,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Exact Mood Song",
            artist="Test Artist",
            genre="rock",
            mood="happy",
            energy=0.4,
            tempo_bpm=100,
            valence=0.4,
            danceability=0.5,
            acousticness=0.2,
        ),
    ]
    rec = Recommender(songs)

    genre_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.4,
        likes_acoustic=False,
        scoring_mode="genre_first",
    )
    mood_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.4,
        likes_acoustic=False,
        scoring_mode="mood_first",
    )

    assert rec.recommend(genre_user, k=2)[0].title == "Exact Genre Song"
    assert rec.recommend(mood_user, k=2)[0].title == "Exact Mood Song"


def test_diversity_penalty_discourages_repeated_artist_in_top_results():
    """Check that the final list avoids repeating the same artist too early."""
    songs = [
        Song(
            id=1,
            title="Artist A Hit",
            artist="Artist A",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.8,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Artist A Followup",
            artist="Artist A",
            genre="pop",
            mood="happy",
            energy=0.79,
            tempo_bpm=119,
            valence=0.79,
            danceability=0.79,
            acousticness=0.2,
        ),
        Song(
            id=3,
            title="Artist B Alternative",
            artist="Artist B",
            genre="indie pop",
            mood="happy",
            energy=0.78,
            tempo_bpm=118,
            valence=0.78,
            danceability=0.78,
            acousticness=0.2,
        ),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )

    results = rec.recommend(user, k=3)

    assert results[0].artist == "Artist A"
    assert results[1].artist == "Artist B"


def test_recommend_raises_for_invalid_k():
    """Check that the recommender rejects non-positive result counts."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    with pytest.raises(ValueError, match="k must be a positive integer"):
        rec.recommend(user, k=0)


def test_score_song_raises_for_out_of_range_energy():
    """Check that invalid energy inputs are stopped before scoring."""
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.5,
        "tempo_bpm": 120.0,
        "valence": 0.7,
        "danceability": 0.7,
        "acousticness": 0.2,
    }

    with pytest.raises(ValueError, match="target_energy must be between 0.0 and 1.0"):
        score_song(
            {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 1.5,
                "likes_acoustic": False,
            },
            song,
        )


def test_recommend_songs_raises_for_empty_required_text_fields():
    """Check that blank genre or mood values are rejected cleanly."""
    songs = [
        {
            "id": 1,
            "title": "Test Song",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.5,
            "tempo_bpm": 120.0,
            "valence": 0.7,
            "danceability": 0.7,
            "acousticness": 0.2,
        }
    ]

    with pytest.raises(ValueError, match="favorite_genre must be a non-empty string"):
        recommend_songs(
            {
                "favorite_genre": "   ",
                "favorite_mood": "happy",
                "target_energy": 0.5,
                "likes_acoustic": False,
            },
            songs,
            k=1,
        )


def test_unknown_scoring_mode_falls_back_to_balanced():
    """Check that unknown scoring modes are normalized to a safe default."""
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120.0,
        "valence": 0.7,
        "danceability": 0.7,
        "acousticness": 0.2,
    }

    _, reasons = score_song(
        {
            "favorite_genre": " POP ",
            "favorite_mood": " HAPPY ",
            "target_energy": 0.8,
            "likes_acoustic": False,
            "scoring_mode": "totally_unknown_mode",
        },
        song,
    )

    assert reasons[0] == "mode=balanced"


def test_recommendation_diagnostics_include_confidence_between_zero_and_one():
    """Check that detailed recommendation results expose a normalized confidence score."""
    songs = [
        {
            "id": 1,
            "title": "Test Song",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120.0,
            "valence": 0.7,
            "danceability": 0.7,
            "acousticness": 0.2,
        }
    ]

    results = recommend_songs_with_diagnostics(
        {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
        },
        songs,
        k=1,
    )

    assert len(results) == 1
    assert 0.0 <= results[0]["confidence"] <= 1.0


def test_low_confidence_diagnostics_add_warning_for_weak_match():
    """Check that weak matches are flagged with cautionary warnings."""
    songs = [
        {
            "id": 1,
            "title": "Soft Mismatch",
            "artist": "Artist",
            "genre": "ambient",
            "mood": "peaceful",
            "energy": 0.52,
            "tempo_bpm": 70.0,
            "valence": 0.5,
            "danceability": 0.3,
            "acousticness": 0.6,
        }
    ]

    results = recommend_songs_with_diagnostics(
        {
            "favorite_genre": "metal",
            "favorite_mood": "rebellious",
            "target_energy": 0.5,
            "likes_acoustic": False,
        },
        songs,
        k=1,
    )

    assert any("Low-confidence recommendation" in warning for warning in results[0]["warnings"])
    assert any("No exact genre or mood match" in warning for warning in results[0]["warnings"])


def test_strong_match_diagnostics_can_avoid_low_confidence_warning():
    """Check that strong direct matches are not automatically flagged as low-confidence."""
    rec = make_small_recommender()
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )

    results = rec.recommend_with_diagnostics(user, k=1)

    assert results[0].confidence >= 0.45
    assert all("Low-confidence recommendation" not in warning for warning in results[0].warnings)
