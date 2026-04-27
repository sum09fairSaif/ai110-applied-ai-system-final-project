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
    return max(lower, min(upper, value))


def _similarity_score(value: float, target: float, max_points: float, scale: float = 1.0) -> float:
    distance = abs(value - target) / scale
    return max(0.0, (1.0 - distance) * max_points)


def _parse_mood_tags(raw_tags: str) -> List[str]:
    if not raw_tags:
        return []
    return [tag.strip().lower() for tag in raw_tags.split("|") if tag.strip()]


def _coalesce(value, fallback):
    return fallback if value is None else value


def _parse_release_decade(raw_value) -> int:
    if isinstance(raw_value, int):
        return raw_value
    cleaned = str(raw_value).strip().lower().replace("s", "")
    return int(cleaned)


def _infer_preference_targets(user_prefs: Dict) -> Dict:
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
    song_dict = asdict(song)
    song_dict["mood_tags"] = song_dict.get("mood_tags", "")
    return song_dict


def _build_weighted_mode(weights: Dict[str, float]) -> ScoringMode:
    def weighted_mode(components: Dict[str, float]) -> float:
        return sum(components.get(name, 0.0) * weight for name, weight in weights.items())

    return weighted_mode


SCORING_STRATEGIES = {
    mode_name: _build_weighted_mode(weights)
    for mode_name, weights in SCORING_MODE_WEIGHTS.items()
}


def get_scoring_mode(mode_name: Optional[str]) -> Tuple[str, ScoringMode]:
    normalized_mode = (mode_name or "balanced").strip().lower()
    return normalized_mode, SCORING_STRATEGIES.get(normalized_mode, SCORING_STRATEGIES["balanced"])


def _score_components(user_prefs: Dict, song: Dict) -> Tuple[Dict[str, float], List[str]]:
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


@dataclass
class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    songs: List[Song]

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs for a user profile."""
        user_prefs = asdict(user)
        ranked = []
        for song in self.songs:
            score, _ = score_song(user_prefs, _song_to_dict(song))
            ranked.append((song, score))

        ranked.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Summarize why a song was recommended for a user."""
        _, reasons = score_song(asdict(user), _song_to_dict(song))
        mode_name, _ = get_scoring_mode(user.scoring_mode)
        summary = ", ".join(reasons) if reasons else "balanced overall fit"
        return f"{mode_name} mode: {summary}"


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """

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
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """

    mode_name, score_strategy = get_scoring_mode(user_prefs.get("scoring_mode"))
    components, reasons = _score_components(user_prefs, song)
    score = score_strategy(components)
    reasons.insert(0, f"mode={mode_name}")
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """

    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
