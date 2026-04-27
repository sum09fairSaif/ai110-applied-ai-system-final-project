from typing import Callable, List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass
import csv


MOOD_TAG_HINTS = {
    "happy": ["uplifting", "bright", "playful"],
    "chill": ["calm", "dreamy", "focused"],
    "intense": ["aggressive", "driving", "epic"],
    "moody": ["nocturnal", "brooding", "cinematic"],
    "focused": ["steady", "minimal", "clear-headed"],
    "relaxed": ["warm", "easygoing", "sunny"],
    "romantic": ["tender", "lush", "intimate"],
    "nostalgic": ["reflective", "vintage", "wistful"],
    "peaceful": ["ambient", "gentle", "spacious"],
    "confident": ["bold", "swagger", "anthemic"],
    "rebellious": ["raw", "loud", "charged"],
    "uplifting": ["hopeful", "bright", "euphoric"],
}

INFERRED_DECADE_BY_GENRE = {
    "pop": 2010,
    "lofi": 2010,
    "rock": 2000,
    "jazz": 1990,
    "ambient": 2010,
    "synthwave": 1980,
    "indie pop": 2010,
    "r&b": 2000,
    "country": 2000,
    "classical": 1990,
    "hip-hop": 2000,
    "metal": 2000,
    "reggae": 1990,
    "folk": 2000,
    "house": 2010,
    "blues": 1990,
    "edm": 2010,
    "k-pop": 2020,
    "americana": 2000,
    "funk": 1980,
    "choral": 1990,
    "trap": 2020,
}

INFERRED_POPULARITY_BY_GENRE = {
    "pop": 78,
    "k-pop": 82,
    "edm": 74,
    "hip-hop": 75,
    "lofi": 46,
    "ambient": 40,
    "classical": 38,
    "rock": 63,
}

INFERRED_REPLAY_BY_MOOD = {
    "happy": 0.78,
    "chill": 0.72,
    "intense": 0.63,
    "moody": 0.68,
    "focused": 0.74,
    "relaxed": 0.70,
    "romantic": 0.66,
}

INFERRED_VOCAL_PREFERENCE = {
    "lofi": 0.35,
    "ambient": 0.20,
    "classical": 0.15,
    "house": 0.55,
    "edm": 0.58,
    "pop": 0.82,
    "r&b": 0.80,
    "hip-hop": 0.88,
    "folk": 0.72,
}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity_0_100: int = 50
    release_decade: int = 2010
    mood_tags: str = ""
    instrumentalness: float = 0.0
    vocal_presence: float = 0.5
    replay_value: float = 0.5


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    target_popularity: Optional[int] = None
    bonus_mood_tags: Optional[List[str]] = None
    prefers_instrumental: Optional[bool] = None
    target_vocal_presence: Optional[float] = None
    target_replay_value: Optional[float] = None
    scoring_mode: str = "balanced"


@dataclass
class RecommendationDiagnostics:
    """Detailed recommendation output with reliability signals for the caller."""

    song: Dict
    score: float
    confidence: float
    explanation: str
    warnings: List[str]
    critique_notes: Optional[List[str]] = None


ScoringMode = Callable[[Dict[str, float]], float]

SCORING_MODE_WEIGHTS = {
    "balanced": {
        "genre_match": 1.0,
        "mood_match": 1.0,
        "energy_similarity": 1.0,
        "acoustic_bonus": 1.0,
        "popularity_fit": 1.0,
        "era_fit": 1.0,
        "mood_tag_overlap": 1.0,
        "instrumental_fit": 1.0,
        "vocal_presence_fit": 1.0,
        "replay_value_fit": 1.0,
    },
    "genre_first": {
        "genre_match": 1.8,
        "mood_match": 0.9,
        "energy_similarity": 0.8,
        "acoustic_bonus": 0.9,
        "popularity_fit": 0.7,
        "era_fit": 0.8,
        "mood_tag_overlap": 0.7,
        "instrumental_fit": 0.7,
        "vocal_presence_fit": 0.8,
        "replay_value_fit": 0.6,
    },
    "mood_first": {
        "genre_match": 0.7,
        "mood_match": 1.8,
        "energy_similarity": 0.9,
        "acoustic_bonus": 0.9,
        "popularity_fit": 0.7,
        "era_fit": 0.7,
        "mood_tag_overlap": 1.6,
        "instrumental_fit": 0.9,
        "vocal_presence_fit": 0.8,
        "replay_value_fit": 0.8,
    },
    "energy_focused": {
        "genre_match": 0.7,
        "mood_match": 0.7,
        "energy_similarity": 1.8,
        "acoustic_bonus": 0.6,
        "popularity_fit": 0.6,
        "era_fit": 0.5,
        "mood_tag_overlap": 0.7,
        "instrumental_fit": 0.6,
        "vocal_presence_fit": 0.6,
        "replay_value_fit": 0.7,
    },
}


def _clamp(value: float, lower: float, upper: float) -> float:
    """Keep a number inside a safe minimum and maximum range."""
    return max(lower, min(upper, value))


def _similarity_score(value: float, target: float, max_points: float, scale: float = 1.0) -> float:
    """Give more points when a song value is close to the user's target value."""
    distance = abs(value - target) / scale
    return max(0.0, (1.0 - distance) * max_points)


def _parse_mood_tags(raw_tags: str) -> List[str]:
    """Split the mood tag text into a clean list of individual tags."""
    if not raw_tags:
        return []
    return [tag.strip().lower() for tag in raw_tags.split("|") if tag.strip()]


def _coalesce(value, fallback):
    """Use the fallback value only when the first value is missing."""
    return fallback if value is None else value


def _parse_release_decade(raw_value) -> int:
    """Convert a decade label like '2010s' into a number the program can compare."""
    if isinstance(raw_value, int):
        return raw_value
    cleaned = str(raw_value).strip().lower().replace("s", "")
    return int(cleaned)


def _infer_preference_targets(user_prefs: Dict) -> Dict:
    """Fill in helpful default preferences when the user did not supply every advanced setting."""
    favorite_genre = user_prefs.get("favorite_genre", "")
    favorite_mood = user_prefs.get("favorite_mood", "")
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    inferred_tags = MOOD_TAG_HINTS.get(favorite_mood, [])
    if likes_acoustic:
        inferred_tags = list(dict.fromkeys([*inferred_tags, "organic", "warm"]))

    return {
        "preferred_decade": _coalesce(
            user_prefs.get("preferred_decade"),
            INFERRED_DECADE_BY_GENRE.get(favorite_genre),
        ),
        "target_popularity": _coalesce(
            user_prefs.get("target_popularity"),
            INFERRED_POPULARITY_BY_GENRE.get(favorite_genre, 58),
        ),
        "bonus_mood_tags": _coalesce(user_prefs.get("bonus_mood_tags"), inferred_tags),
        "prefers_instrumental": _coalesce(
            user_prefs.get("prefers_instrumental"),
            True if favorite_genre in {"lofi", "ambient", "classical"} else None,
        ),
        "target_vocal_presence": _coalesce(
            user_prefs.get("target_vocal_presence"),
            INFERRED_VOCAL_PREFERENCE.get(favorite_genre, 0.65),
        ),
        "target_replay_value": _coalesce(
            user_prefs.get("target_replay_value"),
            INFERRED_REPLAY_BY_MOOD.get(favorite_mood, 0.67),
        ),
    }


def _song_to_dict(song: Song) -> Dict:
    """Convert a Song object into a regular dictionary for easier scoring work."""
    song_dict = asdict(song)
    song_dict["mood_tags"] = song_dict.get("mood_tags", "")
    return song_dict


def _build_weighted_mode(weights: Dict[str, float]) -> ScoringMode:
    """Create a scoring function that combines score parts using the chosen weights."""
    def weighted_mode(components: Dict[str, float]) -> float:
        """Add up the score pieces after multiplying each one by its importance."""
        return sum(components.get(name, 0.0) * weight for name, weight in weights.items())

    return weighted_mode


SCORING_STRATEGIES = {
    mode_name: _build_weighted_mode(weights)
    for mode_name, weights in SCORING_MODE_WEIGHTS.items()
}
VALID_SCORING_MODES = set(SCORING_STRATEGIES)

DIVERSITY_ARTIST_PENALTY = 1.25
DIVERSITY_GENRE_PENALTY = 0.45
LOW_CONFIDENCE_THRESHOLD = 0.50
CRITIQUE_CONFIDENCE_GAP = 0.08
COMPONENT_MAXIMA = {
    "genre_match": 1.0,
    "mood_match": 1.0,
    "energy_similarity": 2.0,
    "acoustic_bonus": 0.5,
    "popularity_fit": 0.75,
    "era_fit": 0.9,
    "mood_tag_overlap": 1.05,
    "instrumental_fit": 0.6,
    "vocal_presence_fit": 0.5,
    "replay_value_fit": 0.45,
}


def get_scoring_mode(mode_name: Optional[str]) -> Tuple[str, ScoringMode]:
    """Choose the scoring style the user asked for, or fall back to the default mode."""
    normalized_mode = (mode_name or "balanced").strip().lower()
    return normalized_mode, SCORING_STRATEGIES.get(normalized_mode, SCORING_STRATEGIES["balanced"])


def _normalize_text(value: object, field_name: str) -> str:
    """Convert a required text field into a clean lowercase string."""
    cleaned = str(value).strip().lower()
    if not cleaned:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return cleaned


def _normalize_optional_float(
    user_prefs: Dict,
    field_name: str,
    lower: float = 0.0,
    upper: float = 1.0,
) -> Optional[float]:
    """Validate an optional float field when the user supplies one."""
    raw_value = user_prefs.get(field_name)
    if raw_value is None:
        return None

    try:
        numeric_value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc

    if not lower <= numeric_value <= upper:
        raise ValueError(f"{field_name} must be between {lower} and {upper}.")
    return numeric_value


def _normalize_optional_int(
    user_prefs: Dict,
    field_name: str,
    lower: int,
    upper: int,
) -> Optional[int]:
    """Validate an optional integer field when the user supplies one."""
    raw_value = user_prefs.get(field_name)
    if raw_value is None:
        return None

    try:
        numeric_value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer.") from exc

    if not lower <= numeric_value <= upper:
        raise ValueError(f"{field_name} must be between {lower} and {upper}.")
    return numeric_value


def validate_user_preferences(user_prefs: Dict) -> Dict:
    """Normalize and validate user preferences before scoring songs."""
    if not isinstance(user_prefs, dict):
        raise ValueError("user_prefs must be a dictionary.")

    favorite_genre = _normalize_text(user_prefs.get("favorite_genre", ""), "favorite_genre")
    favorite_mood = _normalize_text(user_prefs.get("favorite_mood", ""), "favorite_mood")

    try:
        target_energy = float(user_prefs.get("target_energy"))
    except (TypeError, ValueError) as exc:
        raise ValueError("target_energy must be a number between 0.0 and 1.0.") from exc

    if not 0.0 <= target_energy <= 1.0:
        raise ValueError("target_energy must be between 0.0 and 1.0.")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if not isinstance(likes_acoustic, bool):
        raise ValueError("likes_acoustic must be a boolean value.")

    normalized_mode = str(user_prefs.get("scoring_mode", "balanced")).strip().lower() or "balanced"
    if normalized_mode not in VALID_SCORING_MODES:
        normalized_mode = "balanced"

    bonus_mood_tags = user_prefs.get("bonus_mood_tags")
    if bonus_mood_tags is not None:
        if not isinstance(bonus_mood_tags, list):
            raise ValueError("bonus_mood_tags must be a list of strings.")
        normalized_bonus_tags = [
            _normalize_text(tag, "bonus_mood_tags item")
            for tag in bonus_mood_tags
        ]
    else:
        normalized_bonus_tags = None

    prefers_instrumental = user_prefs.get("prefers_instrumental")
    if prefers_instrumental is not None and not isinstance(prefers_instrumental, bool):
        raise ValueError("prefers_instrumental must be a boolean value when provided.")

    preferred_decade = _normalize_optional_int(user_prefs, "preferred_decade", 1900, 2030)
    target_popularity = _normalize_optional_int(user_prefs, "target_popularity", 0, 100)
    target_vocal_presence = _normalize_optional_float(user_prefs, "target_vocal_presence")
    target_replay_value = _normalize_optional_float(user_prefs, "target_replay_value")

    return {
        "favorite_genre": favorite_genre,
        "favorite_mood": favorite_mood,
        "target_energy": target_energy,
        "likes_acoustic": likes_acoustic,
        "preferred_decade": preferred_decade,
        "target_popularity": target_popularity,
        "bonus_mood_tags": normalized_bonus_tags,
        "prefers_instrumental": prefers_instrumental,
        "target_vocal_presence": target_vocal_presence,
        "target_replay_value": target_replay_value,
        "scoring_mode": normalized_mode,
    }


def validate_recommendation_request(user_prefs: Dict, songs: List[Dict], k: int) -> Dict:
    """Validate the inputs for recommendation requests and return normalized preferences."""
    normalized_user_prefs = validate_user_preferences(user_prefs)

    try:
        normalized_k = int(k)
    except (TypeError, ValueError) as exc:
        raise ValueError("k must be a positive integer.") from exc

    if normalized_k <= 0:
        raise ValueError("k must be a positive integer.")

    if not songs:
        raise ValueError("songs must contain at least one song.")

    normalized_user_prefs["k"] = normalized_k
    return normalized_user_prefs


def calculate_max_score_for_mode(mode_name: str) -> float:
    """Estimate the highest achievable score for a scoring mode."""
    weights = SCORING_MODE_WEIGHTS.get(mode_name, SCORING_MODE_WEIGHTS["balanced"])
    return sum(
        COMPONENT_MAXIMA.get(component_name, 0.0) * component_weight
        for component_name, component_weight in weights.items()
    )


def calculate_recommendation_confidence(score: float, mode_name: str) -> float:
    """Normalize a raw score into a 0-1 confidence estimate."""
    max_score = calculate_max_score_for_mode(mode_name)
    if max_score <= 0:
        return 0.0
    return _clamp(score / max_score, 0.0, 1.0)


def build_recommendation_warnings(explanation: str, confidence: float) -> List[str]:
    """Generate caution notes when the match looks weak or indirect."""
    warnings = []

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        warnings.append(
            "Low-confidence recommendation: this match relies more on soft feature similarity than strong direct preference matches."
        )

    if "genre match" not in explanation and "mood match" not in explanation:
        warnings.append(
            "No exact genre or mood match was found, so this recommendation depends on secondary signals."
        )

    return warnings


def run_self_critique_loop(recommendations: List[Dict]) -> List[Dict]:
    """Review recommendations, attach critique notes, and make small trust-oriented adjustments."""
    if not recommendations:
        return []

    critiqued = [dict(item) for item in recommendations]
    critique_notes: List[str] = []
    average_confidence = sum(item["confidence"] for item in critiqued) / len(critiqued)

    if average_confidence < LOW_CONFIDENCE_THRESHOLD:
        critique_notes.append(
            "Self-critique: the overall list has low average confidence, so the results should be treated as exploratory suggestions."
        )

    top_artist = critiqued[0]["song"]["artist"]
    repeated_top_artist = sum(1 for item in critiqued if item["song"]["artist"] == top_artist)
    if repeated_top_artist > 1:
        critique_notes.append(
            "Self-critique: the list leans heavily on one artist, which may reduce discovery diversity."
        )

    if len(critiqued) >= 2:
        first_item = critiqued[0]
        second_item = critiqued[1]
        if (
            first_item["confidence"] < LOW_CONFIDENCE_THRESHOLD
            and second_item["confidence"] - first_item["confidence"] >= CRITIQUE_CONFIDENCE_GAP
        ):
            critiqued[0], critiqued[1] = second_item, first_item
            critique_notes.append(
                "Self-critique: promoted a stronger second recommendation ahead of a weaker top pick."
            )

    for item in critiqued:
        item["critique_notes"] = list(critique_notes)

    return critiqued


def _score_components(user_prefs: Dict, song: Dict) -> Tuple[Dict[str, float], List[str]]:
    """Calculate the individual score pieces for one song before they are combined into a final score."""
    components = {
        "genre_match": 0.0,
        "mood_match": 0.0,
        "energy_similarity": 0.0,
        "acoustic_bonus": 0.0,
        "popularity_fit": 0.0,
        "era_fit": 0.0,
        "mood_tag_overlap": 0.0,
        "instrumental_fit": 0.0,
        "vocal_presence_fit": 0.0,
        "replay_value_fit": 0.0,
    }
    reasons = []
    inferred = _infer_preference_targets(user_prefs)
    song_tags = set(_parse_mood_tags(song.get("mood_tags", "")))

    if song["genre"] == user_prefs.get("favorite_genre"):
        components["genre_match"] = 1.0
        reasons.append("genre match (+1.0)")

    if song["mood"] == user_prefs.get("favorite_mood"):
        components["mood_match"] = 1.0
        reasons.append("mood match (+1.0)")

    energy_score = _similarity_score(
        song["energy"],
        user_prefs.get("target_energy", 0.5),
        max_points=2.0,
    )
    if energy_score > 0:
        components["energy_similarity"] = energy_score
        reasons.append(f"energy similarity (+{energy_score:.2f})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.7:
        components["acoustic_bonus"] = 0.5
        reasons.append("acoustic preference (+0.5)")

    popularity_score = _similarity_score(
        song.get("popularity_0_100", 50),
        inferred["target_popularity"],
        max_points=0.75,
        scale=100.0,
    )
    if popularity_score > 0:
        components["popularity_fit"] = popularity_score
        reasons.append(f"popularity fit (+{popularity_score:.2f})")

    preferred_decade = inferred["preferred_decade"]
    if preferred_decade is not None:
        decade_gap = abs(song.get("release_decade", preferred_decade) - preferred_decade)
        if decade_gap == 0:
            components["era_fit"] = 0.9
            reasons.append("preferred era match (+0.9)")
        elif decade_gap == 10:
            components["era_fit"] = 0.45
            reasons.append("adjacent era bonus (+0.45)")

    matched_tags = song_tags.intersection(tag.lower() for tag in inferred["bonus_mood_tags"])
    if matched_tags:
        tag_score = min(len(matched_tags), 3) * 0.35
        components["mood_tag_overlap"] = tag_score
        reasons.append(f"mood tag overlap (+{tag_score:.2f})")

    prefers_instrumental = inferred["prefers_instrumental"]
    instrumentalness = song.get("instrumentalness", 0.0)
    if prefers_instrumental is True:
        instrumental_score = instrumentalness * 0.6
        if instrumental_score > 0:
            components["instrumental_fit"] = instrumental_score
            reasons.append(f"instrumental bonus (+{instrumental_score:.2f})")
    elif prefers_instrumental is False:
        vocal_forward_score = (1.0 - instrumentalness) * 0.3
        components["instrumental_fit"] = vocal_forward_score
        reasons.append(f"lyric-forward bonus (+{vocal_forward_score:.2f})")

    vocal_score = _similarity_score(
        song.get("vocal_presence", 0.5),
        _clamp(inferred["target_vocal_presence"], 0.0, 1.0),
        max_points=0.5,
    )
    if vocal_score > 0:
        components["vocal_presence_fit"] = vocal_score
        reasons.append(f"vocal presence fit (+{vocal_score:.2f})")

    replay_score = _similarity_score(
        song.get("replay_value", 0.5),
        _clamp(inferred["target_replay_value"], 0.0, 1.0),
        max_points=0.45,
    )
    if replay_score > 0:
        components["replay_value_fit"] = replay_score
        reasons.append(f"replay value fit (+{replay_score:.2f})")

    return components, reasons


def apply_diversity_reranking(
    scored_candidates: List[Tuple[Dict, float, List[str]]],
    k: int,
    artist_penalty: float = DIVERSITY_ARTIST_PENALTY,
    genre_penalty: float = DIVERSITY_GENRE_PENALTY,
) -> List[Tuple[Dict, float, str]]:
    """Build the final top results while lowering the score of repeated artists or genres."""
    selected: List[Tuple[Dict, float, str]] = []
    remaining = scored_candidates[:]
    seen_artists: set[str] = set()
    seen_genres: set[str] = set()

    while remaining and len(selected) < k:
        best_index = 0
        best_adjusted_score = float("-inf")
        best_explanation = "no matches"

        for index, (song, base_score, reasons) in enumerate(remaining):
            adjusted_score = base_score
            adjusted_reasons = list(reasons)

            if song["artist"] in seen_artists:
                adjusted_score -= artist_penalty
                adjusted_reasons.append(f"artist diversity penalty (-{artist_penalty:.2f})")

            if song["genre"] in seen_genres:
                adjusted_score -= genre_penalty
                adjusted_reasons.append(f"genre diversity penalty (-{genre_penalty:.2f})")

            if adjusted_score > best_adjusted_score:
                best_adjusted_score = adjusted_score
                best_index = index
                best_explanation = ", ".join(adjusted_reasons) if adjusted_reasons else "no matches"

        song, _, _ = remaining.pop(best_index)
        selected.append((song, best_adjusted_score, best_explanation))
        seen_artists.add(song["artist"])
        seen_genres.add(song["genre"])

    return selected


@dataclass
class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    songs: List[Song]

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Pick the best songs for a user after scoring them and applying the diversity rules."""
        user_prefs = validate_recommendation_request(
            asdict(user),
            [_song_to_dict(song) for song in self.songs],
            k,
        )
        ranked = []
        for song in self.songs:
            score, reasons = score_song(user_prefs, _song_to_dict(song))
            ranked.append((_song_to_dict(song), score, reasons))

        ranked.sort(key=lambda item: item[1], reverse=True)
        diversified = apply_diversity_reranking(ranked, user_prefs["k"])
        song_by_id = {song.id: song for song in self.songs}
        return [song_by_id[item[0]["id"]] for item in diversified]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in simple text why a song matched this user's preferences."""
        normalized_user = validate_user_preferences(asdict(user))
        _, reasons = score_song(normalized_user, _song_to_dict(song))
        mode_name, _ = get_scoring_mode(normalized_user["scoring_mode"])
        summary = ", ".join(reasons) if reasons else "balanced overall fit"
        return f"{mode_name} mode: {summary}"

    def recommend_with_diagnostics(self, user: UserProfile, k: int = 5) -> List[RecommendationDiagnostics]:
        """Return recommendations together with confidence scores and guardrail warnings."""
        diagnostics = recommend_songs_with_diagnostics(
            asdict(user),
            [_song_to_dict(song) for song in self.songs],
            k=k,
        )
        return [RecommendationDiagnostics(**item) for item in diagnostics]


def load_songs(csv_path: str) -> List[Dict]:
    """Read the song data file and turn each row into a dictionary the recommender can use."""

    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity_0_100": int(row.get("popularity_0_100", 50)),
                "release_decade": _parse_release_decade(row.get("release_decade", 2010)),
                "mood_tags": row.get("mood_tags", ""),
                "instrumentalness": float(row.get("instrumentalness", 0.0)),
                "vocal_presence": float(row.get("vocal_presence", 0.5)),
                "replay_value": float(row.get("replay_value", 0.5)),
            }
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Give one song a score by comparing its features to what the user likes."""
    user_prefs = validate_user_preferences(user_prefs)
    mode_name, score_strategy = get_scoring_mode(user_prefs.get("scoring_mode"))
    components, reasons = _score_components(user_prefs, song)
    score = score_strategy(components)
    reasons.insert(0, f"mode={mode_name}")
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort them, and return the best few with short explanations."""
    normalized_user_prefs = validate_recommendation_request(user_prefs, songs, k)
    scored = []
    for song in songs:
        score, reasons = score_song(normalized_user_prefs, song)
        scored.append((song, score, reasons))

    scored.sort(key=lambda item: item[1], reverse=True)
    return apply_diversity_reranking(scored, normalized_user_prefs["k"])


def recommend_songs_with_diagnostics(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Dict]:
    """Return recommendation results with confidence estimates and caution warnings."""
    normalized_user_prefs = validate_recommendation_request(user_prefs, songs, k)
    ranked_results = recommend_songs(normalized_user_prefs, songs, k=normalized_user_prefs["k"])
    mode_name = normalized_user_prefs["scoring_mode"]
    diagnostics = []

    for song, score, explanation in ranked_results:
        confidence = calculate_recommendation_confidence(score, mode_name)
        warnings = build_recommendation_warnings(explanation, confidence)
        diagnostics.append(
            {
                "song": song,
                "score": score,
                "confidence": confidence,
                "explanation": explanation,
                "warnings": warnings,
            }
        )

    return run_self_critique_loop(diagnostics)
