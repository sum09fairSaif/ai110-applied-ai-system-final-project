"""Shared user profiles for demos and evaluation."""

USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "scoring_mode": "genre_first",
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "likes_acoustic": True,
        "scoring_mode": "mood_first",
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "scoring_mode": "energy_focused",
    },
    "Conflicting High-Energy Moody": {
        "favorite_genre": "pop",
        "favorite_mood": "moody",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "scoring_mode": "mood_first",
    },
    "No Categorical Matches": {
        "favorite_genre": "jazz",
        "favorite_mood": "focused",
        "target_energy": 0.5,
        "likes_acoustic": True,
        "scoring_mode": "balanced",
    },
    "Boundary Low Energy": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.0,
        "likes_acoustic": False,
        "scoring_mode": "energy_focused",
    },
    "Boundary High Energy": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 1.0,
        "likes_acoustic": False,
        "scoring_mode": "energy_focused",
    },
    "Perfect Match with Acoustic": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "likes_acoustic": True,
        "scoring_mode": "genre_first",
    },
}
