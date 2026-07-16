"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


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

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:")
    print("=" * 50)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — Score: {score:.2f}")
        print("-" * 50)
        for reason in explanation.split("; "):
            print(f"  - {reason}")
        print("=" * 50)


if __name__ == "__main__":
    main()
