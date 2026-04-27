"""Streamlit UI for the MusixxMatch music recommender."""

from __future__ import annotations

from pathlib import Path
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from logging_utils import append_jsonl_log, build_recommendation_log_entry
from profiles import USER_PROFILES
from recommender import load_songs, recommend_songs_with_diagnostics


APP_TITLE = "MusixxMatch"
DEFAULT_DATA_PATH = Path("data") / "songs.csv"


@st.cache_data(show_spinner=False)
def get_song_catalog(csv_path: str = str(DEFAULT_DATA_PATH)) -> list[dict]:
    """Load and cache the song catalog for the UI session."""
    return load_songs(csv_path)


def build_user_preferences(
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    likes_acoustic: bool,
    scoring_mode: str,
    preferred_decade: int | None = None,
    target_popularity: int | None = None,
    prefers_instrumental: bool | None = None,
) -> dict:
    """Normalize Streamlit widget values into the recommender input shape."""
    return {
        "favorite_genre": favorite_genre,
        "favorite_mood": favorite_mood,
        "target_energy": float(target_energy),
        "likes_acoustic": bool(likes_acoustic),
        "scoring_mode": scoring_mode,
        "preferred_decade": preferred_decade,
        "target_popularity": target_popularity,
        "prefers_instrumental": prefers_instrumental,
    }


def recommendations_to_dataframe(recommendations: list[dict]) -> pd.DataFrame:
    """Convert recommendation diagnostics into a table-friendly DataFrame."""
    rows = []
    for rank, result in enumerate(recommendations, 1):
        rows.append(
            {
                "Rank": rank,
                "Title": result["song"]["title"],
                "Artist": result["song"]["artist"],
                "Genre": result["song"]["genre"],
                "Mood": result["song"]["mood"],
                "Score": round(result["score"], 2),
                "Confidence": round(result["confidence"], 2),
                "Warnings": " | ".join(result["warnings"]) if result["warnings"] else "None",
                "Critique": " | ".join(result.get("critique_notes", [])) if result.get("critique_notes") else "None",
            }
        )
    return pd.DataFrame(rows)


def preset_names() -> list[str]:
    """Return the selectable profile preset names for the UI."""
    return ["Custom"] + list(USER_PROFILES.keys())


def render_sidebar_summary(songs: list[dict]) -> None:
    """Show dataset-level context in the sidebar."""
    genres = sorted({song["genre"] for song in songs})
    moods = sorted({song["mood"] for song in songs})

    st.sidebar.header("Catalog Snapshot")
    st.sidebar.metric("Songs", len(songs))
    st.sidebar.metric("Genres", len(genres))
    st.sidebar.metric("Moods", len(moods))
    st.sidebar.caption("MusixxMatch uses explainable scoring, confidence estimates, warnings, and a self-critique pass.")


def render_recommendation_cards(recommendations: list[dict]) -> None:
    """Display detailed recommendation results in an easy-to-scan layout."""
    for rank, result in enumerate(recommendations, 1):
        song = result["song"]
        with st.container(border=True):
            st.subheader(f"{rank}. {song['title']} - {song['artist']}")
            st.write(
                f"Genre: `{song['genre']}` | Mood: `{song['mood']}` | "
                f"Score: `{result['score']:.2f}` | Confidence: `{result['confidence']:.2f}`"
            )
            st.write(f"Why it matched: {result['explanation']}")

            if result["warnings"]:
                st.warning("Warnings: " + " ".join(result["warnings"]))
            else:
                st.success("Warnings: None")

            critique_notes = result.get("critique_notes", [])
            if critique_notes:
                st.info(" ".join(critique_notes))
            else:
                st.caption("Self-critique: None")


def main() -> None:
    """Run the MusixxMatch Streamlit application."""
    st.set_page_config(page_title=APP_TITLE, page_icon="🎵", layout="wide")
    st.title(APP_TITLE)
    st.caption("An explainable music recommender with confidence scores, guardrails, logging, evaluation, and self-critique.")

    songs = get_song_catalog()
    render_sidebar_summary(songs)

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("Listener Profile")
        selected_preset = st.selectbox("Profile preset", preset_names(), index=0)
        preset = USER_PROFILES.get(selected_preset, {})

        available_genres = sorted({song["genre"] for song in songs})
        available_moods = sorted({song["mood"] for song in songs})
        scoring_modes = ["balanced", "genre_first", "mood_first", "energy_focused"]
        decade_options = [None, 1980, 1990, 2000, 2010, 2020]

        default_genre = preset.get("favorite_genre", available_genres[0])
        default_mood = preset.get("favorite_mood", available_moods[0])
        default_mode = preset.get("scoring_mode", "balanced")

        favorite_genre = st.selectbox(
            "Favorite genre",
            available_genres,
            index=available_genres.index(default_genre) if default_genre in available_genres else 0,
        )
        favorite_mood = st.selectbox(
            "Favorite mood",
            available_moods,
            index=available_moods.index(default_mood) if default_mood in available_moods else 0,
        )
        target_energy = st.slider(
            "Target energy",
            min_value=0.0,
            max_value=1.0,
            value=float(preset.get("target_energy", 0.5)),
            step=0.05,
        )
        likes_acoustic = st.checkbox("Likes acoustic songs", value=bool(preset.get("likes_acoustic", False)))
        scoring_mode = st.selectbox(
            "Scoring mode",
            scoring_modes,
            index=scoring_modes.index(default_mode) if default_mode in scoring_modes else 0,
        )
        preferred_decade = st.selectbox(
            "Preferred decade",
            decade_options,
            index=decade_options.index(preset.get("preferred_decade")) if preset.get("preferred_decade") in decade_options else 0,
            format_func=lambda value: "Auto infer" if value is None else f"{value}s",
        )
        target_popularity = st.slider(
            "Target popularity",
            min_value=0,
            max_value=100,
            value=int(preset.get("target_popularity", 58)),
            step=1,
        )
        instrumental_choice = st.selectbox(
            "Instrumental preference",
            ["Auto infer", "Prefer instrumental", "Prefer vocals"],
            index=0,
        )
        recommendation_count = st.slider("How many recommendations?", min_value=3, max_value=8, value=5, step=1)

        if instrumental_choice == "Prefer instrumental":
            prefers_instrumental = True
        elif instrumental_choice == "Prefer vocals":
            prefers_instrumental = False
        else:
            prefers_instrumental = None

        user_prefs = build_user_preferences(
            favorite_genre=favorite_genre,
            favorite_mood=favorite_mood,
            target_energy=target_energy,
            likes_acoustic=likes_acoustic,
            scoring_mode=scoring_mode,
            preferred_decade=preferred_decade,
            target_popularity=target_popularity,
            prefers_instrumental=prefers_instrumental,
        )

        run_button = st.button("Find My Matches", type="primary", use_container_width=True)

    with right_col:
        st.subheader("How MusixxMatch Thinks")
        st.markdown(
            """
            - Scores songs by genre, mood, energy, popularity, era, and other catalog features.
            - Estimates confidence from the match strength for the selected scoring mode.
            - Warns when the system is relying on weak or indirect signals.
            - Runs a self-critique pass to flag low-confidence lists or repetition concerns.
            """
        )

    if run_button:
        try:
            recommendations = recommend_songs_with_diagnostics(user_prefs, songs, k=recommendation_count)
            log_entry = build_recommendation_log_entry(
                selected_preset if selected_preset != "Custom" else "Custom MusixxMatch Session",
                user_prefs,
                recommendations,
            )
            log_path = append_jsonl_log(log_entry)

            st.success(f"Generated {len(recommendations)} recommendations.")
            st.caption(f"Session log saved to `{log_path}`")

            top_confidence = max(item["confidence"] for item in recommendations)
            low_confidence_total = sum(
                1 for item in recommendations
                if any("Low-confidence recommendation" in warning for warning in item["warnings"])
            )

            metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
            metric_col_1.metric("Top confidence", f"{top_confidence:.2f}")
            metric_col_2.metric("Low-confidence picks", low_confidence_total)
            metric_col_3.metric("Unique genres", len({item["song"]["genre"] for item in recommendations}))

            st.subheader("Recommendation Table")
            st.dataframe(recommendations_to_dataframe(recommendations), use_container_width=True, hide_index=True)

            st.subheader("Detailed Matches")
            render_recommendation_cards(recommendations)
        except ValueError as exc:
            st.error(f"Could not generate recommendations: {exc}")


if __name__ == "__main__":
    main()
