"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
import os
import textwrap
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs

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
    "Conflicting High-Energy Moody": {
        "favorite_genre": "pop",
        "favorite_mood": "moody",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "No Categorical Matches": {
        "favorite_genre": "jazz",
        "favorite_mood": "focused",
        "target_energy": 0.5,
        "likes_acoustic": True,
    },
    "Boundary Low Energy": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.0,
        "likes_acoustic": False,
    },
    "Boundary High Energy": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 1.0,
        "likes_acoustic": False,
    },
    "Perfect Match with Acoustic": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "likes_acoustic": True,
    },
}


def format_recommendation_table(recommendations: list[tuple[dict, float, str]]) -> str:
    """Format recommendations as a simple ASCII table for terminal output."""
    headers = ["Rank", "Title", "Artist", "Score", "Reasons"]
    max_widths = [4, 22, 18, 5, 55]
    rows = []

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        rows.append([
            str(rank),
            song["title"],
            song["artist"],
            f"{score:.2f}",
            explanation,
        ])

    widths = []
    for col_idx, header in enumerate(headers):
        cell_width = max(len(row[col_idx]) for row in rows) if rows else 0
        widths.append(min(max(len(header), cell_width), max_widths[col_idx]))

    def wrap_cell(value: str, width: int) -> list[str]:
        wrapped = textwrap.wrap(value, width=width, break_long_words=False)
        return wrapped or [""]

    def make_row_lines(values: list[str]) -> list[str]:
        wrapped_columns = [wrap_cell(value, widths[idx]) for idx, value in enumerate(values)]
        row_height = max(len(column) for column in wrapped_columns)
        lines = []

        for line_idx in range(row_height):
            line_values = []
            for col_idx, column in enumerate(wrapped_columns):
                cell_value = column[line_idx] if line_idx < len(column) else ""
                line_values.append(cell_value.ljust(widths[col_idx]))
            lines.append("| " + " | ".join(line_values) + " |")

        return lines

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    lines = [separator]
    lines.extend(make_row_lines(headers))
    lines.append(separator)
    for row in rows:
        lines.extend(make_row_lines(row))
    lines.append(separator)
    return "\n".join(lines)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for profile_name, user_prefs in USER_PROFILES.items():
        print(f"\n--- Profile: {profile_name} ---")
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nTop recommendations:\n")
        print(format_recommendation_table(recommendations))


if __name__ == "__main__":
    main()
