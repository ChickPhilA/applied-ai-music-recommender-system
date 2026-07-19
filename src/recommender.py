import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    target_danceability: float
    target_acousticness: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dictionaries with numeric fields converted."""
    songs = []
    with open(csv_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append({
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
            })
    return songs

FEATURE_MAX_POINTS = {
    "energy": 3.0,
    "valence": 2.0,
    "danceability": 2.0,
    "acousticness": 2.0,
}

ACOUSTIC_BONUS_THRESHOLD = 0.5
ACOUSTIC_BONUS_POINTS = 1.0


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song against user preferences using genre/mood matches and feature closeness."""
    score = 0.0
    reasons = []

    if "genre" in user_prefs and song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append(f"Genre matches ({song['genre']}) +2.0")

    if "mood" in user_prefs and song["mood"] == user_prefs["mood"]:
        score += 1.0
        reasons.append(f"Mood matches ({song['mood']}) +1.0")

    for feature, max_points in FEATURE_MAX_POINTS.items():
        if feature not in user_prefs:
            continue
        # Clamp so preference values outside [0, 1] can't push a song's score negative.
        closeness = max(0.0, 1 - abs(song[feature] - user_prefs[feature]))
        points = closeness * max_points
        score += points
        reasons.append(f"{feature.capitalize()} closeness {closeness:.2f} (+{points:.2f})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= ACOUSTIC_BONUS_THRESHOLD:
        score += ACOUSTIC_BONUS_POINTS
        reasons.append(f"Likes acoustic music and song is acoustic (+{ACOUSTIC_BONUS_POINTS:.2f})")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song against user preferences and returns the top k, ranked highest to lowest."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in scored[:k]]
