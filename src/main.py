"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs

USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv") 
    print(f"Loaded songs: {len(songs)}")

    # Pick one profile to test in the CLI output.
    user_prefs = USER_PROFILES["High-Energy Pop"]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"{i}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print("-" * 50)


if __name__ == "__main__":
    main()
