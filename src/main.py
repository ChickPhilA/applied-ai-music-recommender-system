"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def print_recommendations(title: str, recommendations) -> None:
    print(f"\n{title}")
    print("=" * 50)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — Score: {score:.2f}")
        print("-" * 50)
        for reason in explanation.split("; "):
            print(f"  - {reason}")
        print("=" * 50)


# Adversarial / edge case profiles used to stress-test the scoring logic.
# See README.md's "Adversarial / Edge Case Testing" section for full results.
ADVERSARIAL_PROFILES = {
    "1. Conflicted (pop/sad, high energy)": {
        "genre": "pop", "mood": "sad",
        "energy": 0.9, "valence": 0.9,
        "danceability": 0.8, "acousticness": 0.1,
        "likes_acoustic": False,
    },
    "2. likes_acoustic contradiction": {
        "genre": "lofi", "mood": "chill",
        "acousticness": 0.0,
        "likes_acoustic": True,
    },
    "3. Empty profile": {},
    "4. Case-sensitivity typo": {
        "genre": "Pop", "mood": "Happy", "energy": 0.8,
    },
    "5. Out-of-range values": {
        "energy": 1.8, "valence": -0.5,
    },
    "6. Single-feature only": {
        "energy": 0.5,
    },
    "7. Unknown/extra key (tempo_bpm)": {
        "genre": "rock", "tempo_bpm": 140,
    },
    "8. Perfect opposite": {
        "genre": "none-existing-genre", "mood": "none-existing-mood",
        "energy": 0.0, "valence": 0.0, "danceability": 0.0, "acousticness": 0.0,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.2,
        "likes_acoustic": False,
    }
    user_prefs2 = {
        "genre": "indie",
        "mood": "upbeat",
        "energy": 0.6,
        "valence": 0.6,
        "danceability": 0.5,
        "acousticness": 0.5,
        "likes_acoustic": True,
    }
    # High-Energy Pop
    user_prefs3 = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "valence": 0.85,
        "danceability": 0.85,
        "acousticness": 0.1,
        "likes_acoustic": False,
    }
    # Chill Lofi
    user_prefs4 = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "valence": 0.55,
        "danceability": 0.55,
        "acousticness": 0.85,
        "likes_acoustic": True,
    }
    # Deep Intense Rock
    user_prefs5 = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "valence": 0.45,
        "danceability": 0.6,
        "acousticness": 0.1,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations("Top recommendations:", recommendations)

    print("\n\nAdversarial / Edge Case Profiles")
    print("#" * 50)
    for name, prefs in ADVERSARIAL_PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(f"{name}\nprefs: {prefs}", recs)


if __name__ == "__main__":
    main()
