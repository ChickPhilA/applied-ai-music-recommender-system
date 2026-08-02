from src.agent import compute_confidence, plan_and_recommend
from src.main import ADVERSARIAL_PROFILES
from src.recommender import load_songs

SONGS = load_songs("data/songs.csv")


def test_compute_confidence_low_coverage():
    assert compute_confidence(coverage=0.1, margin=5.0) == "low"


def test_compute_confidence_low_margin():
    assert compute_confidence(coverage=0.9, margin=0.1) == "low"


def test_compute_confidence_high():
    assert compute_confidence(coverage=0.8, margin=2.0) == "high"


def test_compute_confidence_medium():
    assert compute_confidence(coverage=0.5, margin=0.8) == "medium"


def test_profile_1_conflicted_flags_low_confidence_top_pick():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["1. Conflicted (pop/sad, high energy)"], SONGS, k=5)

    top_song, _, _, confidence = result.recommendations[0]
    assert confidence == "low"
    assert any("self-critique" in entry["detail"].lower() for entry in result.log)


def test_profile_2_contradiction_is_logged():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["2. likes_acoustic contradiction"], SONGS, k=5)

    assert any("contradiction" in entry["detail"].lower() for entry in result.log)


def test_profile_3_empty_profile_forces_low_confidence_and_is_logged():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["3. Empty profile"], SONGS, k=5)

    assert any("empty" in entry["detail"].lower() for entry in result.log)
    assert all(confidence == "low" for _, _, _, confidence in result.recommendations)


def test_profile_4_case_typo_is_normalized_to_full_match():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["4. Case-sensitivity typo"], SONGS, k=5)

    _, score, explanation, _ = next(r for r in result.recommendations if r[0]["title"] == "Sunrise City")
    assert "Genre matches" in explanation
    assert "Mood matches" in explanation
    assert any(entry["step"] == "normalize" for entry in result.log)


def test_profile_5_out_of_range_values_are_clamped_and_nonnegative():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["5. Out-of-range values"], SONGS, k=5)

    assert any("clamped" in entry["detail"].lower() for entry in result.log)
    assert all(score >= 0.0 for _, score, _, _ in result.recommendations)


def test_profile_6_single_feature_is_low_confidence_sparse_profile():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["6. Single-feature only"], SONGS, k=5)

    assert all(confidence == "low" for _, _, _, confidence in result.recommendations)


def test_profile_7_unknown_key_is_logged_as_unsupported():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["7. Unknown/extra key (tempo_bpm)"], SONGS, k=5)

    assert any("tempo_bpm" in entry["detail"] for entry in result.log)


def test_profile_8_perfect_opposite_still_returns_nonnegative_scores():
    result = plan_and_recommend(ADVERSARIAL_PROFILES["8. Perfect opposite"], SONGS, k=5)

    assert len(result.recommendations) == 5
    assert all(score >= 0.0 for _, score, _, _ in result.recommendations)
