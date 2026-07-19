from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
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


def make_acoustic_song() -> dict:
    return {
        "id": 1,
        "title": "Quiet Room",
        "artist": "Test Artist",
        "genre": "folk",
        "mood": "peaceful",
        "energy": 0.2,
        "tempo_bpm": 70,
        "valence": 0.5,
        "danceability": 0.3,
        "acousticness": 0.9,
    }


def test_likes_acoustic_gives_bonus_for_acoustic_song():
    song = make_acoustic_song()
    score_with_preference, reasons_with = score_song({"likes_acoustic": True}, song)
    score_without_preference, _ = score_song({"likes_acoustic": False}, song)

    assert score_with_preference > score_without_preference
    assert any("acoustic" in reason.lower() for reason in reasons_with)


def test_likes_acoustic_gives_no_bonus_for_non_acoustic_song():
    loud_song = make_acoustic_song()
    loud_song["acousticness"] = 0.1

    score, reasons = score_song({"likes_acoustic": True}, loud_song)

    assert score == 0.0
    assert not any("acoustic" in reason.lower() for reason in reasons)


def test_score_song_clamps_out_of_range_preferences_to_nonnegative():
    song = make_acoustic_song()

    # A target energy above the valid [0, 1] range used to make closeness go
    # negative and drag a song's score below zero.
    score, reasons = score_song({"energy": 1.8}, song)

    assert score >= 0.0
    assert "closeness -" not in " ".join(reasons)
