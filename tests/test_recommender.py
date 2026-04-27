from src.recommender import Song, UserProfile, Recommender

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
