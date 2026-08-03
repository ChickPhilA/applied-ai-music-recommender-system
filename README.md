# 🎵 Harmo-Vibe: Agentic Music Recommender

## Original Project (CodePath AI 110 - Project/Show 3)

This project started as Harmo-Vibe, a rule based music recommender built for my CodePath AI 110 Project 3. The original goal was simple: take a small catalog of songs and a user's stated music taste, then score and rank songs by how closely they matched. Along the way I stress tested the scoring logic against tricky user profiles and found and fixed a couple of real bugs, which taught me a lot about how easily a recommender can quietly behave in ways you did not expect.

## Project Summary

Harmo-Vibe recommends songs by comparing a song's audio features, like energy, mood, and danceability, against what a user says they like, then ranking the closest matches. For this final project, I extended it with an agentic loop that sits in front of the original scoring logic. Before it even scores anything, the system now cleans up messy input and notices obvious problems in a user's profile, and after it ranks the songs, it rates how confident it actually is in its own top pick instead of just handing back an answer with false certainty.

---

## Architecture Overview

The full system diagram lives at [`diagrams/architecture.mmd`](diagrams/architecture.mmd). In short, the song data and a user's preferences flow into the agent, which first cleans up and checks the input, then hands things off to the original scoring engine to rank songs, then looks at its own top pick and rates how confident it is before anything gets printed. Two separate test files sit alongside this, one checking the scoring engine on its own, and one checking the agent's behavior specifically.

## How The System Works

Explain your design in plain language.

**The two most common filtering methods for suggestions when it comes to selecting what type of media should be shown to a user, are content-based filtering and collaborative filtering. Content-based filtering emphasizes certain details and characteristics of its media while collaborative filtering is dependent on other users that have similar scoring suggestions. Real world applications, such as YouTube or Spotify, use a hybrid of both filtering methods. This includes a 'taste graph', content-based audio-embedding models, session-based models, and contextual signals (based on a user's behavior).** 

**In this project, our version will prioritize key features provided for us, given a song and its features with its own score, on a scale from 0.0 to 1.0. To score a song, we use a formula that subtracts the absolute value of the difference between a song's feature value and the user's preference for that feature, from 1 (score = 1 - |song value - user preference|). The user's preference for each feature comes from averaging that feature across every song the user has liked, giving us a centroid, which is one point representing the user's overall taste. Each new candidate song is then compared against this centroid, and the closer a song's features are to the centroid, the higher its score. Ultimately, we rank recommended songs from smallest distance (best match) to largest distance (worst match) from the centroid.**

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
    -  **Features that each `Song` uses in our system are energy, valence, danceability, acousticness, and tempo_bpm.**
- What information does your `UserProfile` store
  - **Our `UserProfile` stores information descripting data variables on a user's favortie genre, mood, their target energy score, and if they like acoustic-featured music.**
- How does your `Recommender` compute a score for each song
  -**Our recommended will compute a score for each song by subtracting the absolute value of the difference between the song's feature value and user preference score, from 1..**
- How do you choose which songs to recommend
  -**Songs will be recommended based on a ranking system. The user will have an average score that represents their overall taste on a feature, acting as a centroid. Songs being recommended will be scored from highest to lowest, based on how close their score is to the centroid value.**

You can include a simple diagram or bullet list if helpful.

### Algorithm Recipe

1. **Represent each song as feature values** — genre, mood (categorical), plus energy, valence, danceability, acousticness, and tempo (numeric, scaled 0.0–1.0).
2. **Build the user's centroid** — average the numeric features across the songs a user has liked (or, in our current starter profiles, set these target values directly). This centroid represents the user's overall taste, e.g. `[energy=0.6, valence=0.6, danceability=0.5, acousticness=0.5]`.
3. **Score each candidate song against the centroid:**
   - **Genre match** → +2.0 points if the song's genre matches the user's favorite genre, else +0.
   - **Mood match** → +1.0 point if the song's mood matches the user's favorite mood, else +0.
   - **Numeric closeness** → for each numeric feature, compute `closeness = 1 - |song value - user preference|`, then convert to points by multiplying by that feature's max point value (e.g. `closeness_energy × 3.0`).
4. **Add up all the points** into one `total_points` score per song.
5. **Rank songs by `total_points`**, highest to lowest, and return the top `k` as recommendations.

### Agentic Loop & Confidence Scoring

On top of the scoring engine above, `src/agent.py` wraps every recommendation request in a small agentic loop that plans, acts, and checks its own work, implemented as plain deterministic Python (no live LLM calls needed for this):

1. **Plan** — normalize the incoming preferences (lowercase `genre`/`mood` so casing typos don't silently fail to match, clamp any numeric target back into `[0, 1]`), then detect known problem patterns: an empty profile, a contradictory `likes_acoustic` flag, or unsupported keys like `tempo_bpm`. Every change or detection gets logged.
2. **Act** — call the existing `recommend_songs()` scoring logic unchanged.
3. **Check its own work** — for each returned song, compute a confidence label (`low`, `medium`, or `high`) from how much of the profile was actually specified and how close the score is to the next-ranked song. If the #1 pick comes back low confidence, the agent logs a self-critique warning flagging it.

This is what actually catches the mood mismatch bug we found by hand below (Profile 1): the agent flags its own top pick as low confidence instead of presenting it with false certainty. See `tests/test_agent.py` for the automated tests covering this behavior.

### Design Decisions

I chose a deterministic Python design over a live LLM or API call mainly because of project constraints. I wanted the agent's choices to be clear and left or right, meaning either a rule fires or it does not, rather than something ambiguous that also costs API credits just to clean up a user profile. This gave me a much clearer picture of exactly what the system was doing and why, instead of leaving that decision making up to a model I could not fully predict.

I also added a confidence rating because a single score by itself can be misleading. A number alone cannot tell you if it is trustworthy 100 percent of the time. By looking at the margin between songs and how close a song actually is to what the user asked for, the confidence rating gives a better sense of how far apart or how close the underlying data really is, and what that distance actually means for how much you should trust the ranking.

### Potential Biases to Watch For

- **Popularity/genre skew:** genre match is weighted heavily (+2.0), so songs in the user's favorite genre could dominate recommendations even when a differently-labeled song is a closer overall match — narrowing exposure over time.
- **Catalog bias:** our dataset is small and hand-picked, so certain genres/moods are represented more than others, which can make the recommender look more "confident" about some tastes than others simply due to data availability, not real fit.
- **Cold-start bias:** users with no liked-song history (or only a couple of liked songs) get a centroid built from very little data, which can produce narrow or skewed recommendations until more preference data is collected.
- **Feature bias:** the numeric features we score on (energy, valence, danceability, acousticness) don't capture everything about a song (e.g. lyrics, cultural context, instrumentation) — so two songs that "feel" different to a human listener could still score as very close matches.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the tests with:

```bash
python -m pytest
```

(Note: bare `pytest` will fail with `ModuleNotFoundError: No module named 'src'` since there's no `conftest.py` — always run it as `python -m pytest` so the project root is on the path.)

Tests live in `tests/test_recommender.py` (core scoring logic) and `tests/test_agent.py` (the agentic loop's plan/detect/self-critique behavior, covering the 8 adversarial profiles below).

---

## Execution Evidence

Real output from an actual run, so the system can be checked without watching a video.

### Command and input

```bash
python -m src.main
```

Runs the default profile (`genre=pop, mood=happy, energy=0.8, valence=0.8, danceability=0.8, acousticness=0.2`) followed by the 8 adversarial profiles defined in `ADVERSARIAL_PROFILES` inside `src/main.py`.

### Output: default profile, high confidence top pick

```
Top recommendations:
==================================================
1. Sunrise City — Score: 11.80 — Confidence: high
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Mood matches (happy) +1.0
  - Energy closeness 0.98 (+2.94)
  - Valence closeness 0.96 (+1.92)
  - Danceability closeness 0.99 (+1.98)
  - Acousticness closeness 0.98 (+1.96)
==================================================
2. Gym Hero — Score: 10.09 — Confidence: medium
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.87 (+2.61)
  - Valence closeness 0.97 (+1.94)
  - Danceability closeness 0.92 (+1.84)
  - Acousticness closeness 0.85 (+1.70)
==================================================
```

### Guardrail result: agent catches a mismatched top pick on its own

Input: `{'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.9, 'danceability': 0.8, 'acousticness': 0.1, 'likes_acoustic': False}`

```
1. Conflicted (pop/sad, high energy)
prefs: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.9, 'danceability': 0.8, 'acousticness': 0.1, 'likes_acoustic': False}
Agent log:
  [check] Self-critique: top pick 'Sunrise City' has low confidence — treat this ranking with caution.
==================================================
1. Sunrise City — Score: 10.46 — Confidence: low
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.92 (+2.76)
  - Valence closeness 0.94 (+1.88)
  - Danceability closeness 0.99 (+1.98)
  - Acousticness closeness 0.92 (+1.84)
==================================================
2. Gym Hero — Score: 10.39 — Confidence: high
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.97 (+2.91)
  - Valence closeness 0.87 (+1.74)
  - Danceability closeness 0.92 (+1.84)
  - Acousticness closeness 0.95 (+1.90)
==================================================
```

`Sunrise City` is mood `happy`, not `sad`, and the agent flags it as low confidence on its own instead of presenting it with false certainty.

### Guardrail result: agent detects a contradictory profile

Input: `{'genre': 'lofi', 'mood': 'chill', 'acousticness': 0.0, 'likes_acoustic': True}`

```
2. likes_acoustic contradiction
prefs: {'genre': 'lofi', 'mood': 'chill', 'acousticness': 0.0, 'likes_acoustic': True}
Agent log:
  [detect] Contradiction: likes_acoustic=True but acousticness target is 0.0 (low). Scoring both signals as given.
  [check] Self-critique: top pick 'Midnight Coding' has low confidence — treat this ranking with caution.
==================================================
1. Midnight Coding — Score: 4.58 — Confidence: low
--------------------------------------------------
  - Genre matches (lofi) +2.0
  - Mood matches (chill) +1.0
  - Acousticness closeness 0.29 (+0.58)
  - Likes acoustic music and song is acoustic (+1.00)
==================================================
```

### Command and reliability results: full test suite

```bash
python -m pytest -v
```

```
tests/test_agent.py::test_compute_confidence_low_coverage PASSED         [  5%]
tests/test_agent.py::test_compute_confidence_low_margin PASSED           [ 11%]
tests/test_agent.py::test_compute_confidence_high PASSED                 [ 17%]
tests/test_agent.py::test_compute_confidence_medium PASSED               [ 23%]
tests/test_agent.py::test_profile_1_conflicted_flags_low_confidence_top_pick PASSED [ 29%]
tests/test_agent.py::test_profile_2_contradiction_is_logged PASSED       [ 35%]
tests/test_agent.py::test_profile_3_empty_profile_forces_low_confidence_and_is_logged PASSED [ 41%]
tests/test_agent.py::test_profile_4_case_typo_is_normalized_to_full_match PASSED [ 47%]
tests/test_agent.py::test_profile_5_out_of_range_values_are_clamped_and_nonnegative PASSED [ 52%]
tests/test_agent.py::test_profile_6_single_feature_is_low_confidence_sparse_profile PASSED [ 58%]
tests/test_agent.py::test_profile_7_unknown_key_is_logged_as_unsupported PASSED [ 64%]
tests/test_agent.py::test_profile_8_perfect_opposite_still_returns_nonnegative_scores PASSED [ 70%]
tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score FAILED [ 76%]
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string FAILED [ 82%]
tests/test_recommender.py::test_likes_acoustic_gives_bonus_for_acoustic_song PASSED [ 88%]
tests/test_recommender.py::test_likes_acoustic_gives_no_bonus_for_non_acoustic_song PASSED [ 94%]
tests/test_recommender.py::test_score_song_clamps_out_of_range_preferences_to_nonnegative PASSED [100%]

========================= 2 failed, 15 passed in 0.06s =========================
```

The 2 failures are in the pre-existing, out-of-scope `Recommender`/`UserProfile` class stub from the Project 3 starter template (it was never implemented, see `src/recommender.py`), unrelated to the agentic workflow added for this final project. All 12 agent tests and all 3 original scoring tests pass.

---

## Sample Recommendation Output

Output from `python -m src.main` for the default "pop/happy" profile (`genre=pop, mood=happy, energy=0.8, valence=0.8, danceability=0.8, acousticness=0.2`):

```
Loaded songs: 20

Top recommendations:
==================================================
1. Sunrise City — Score: 11.80
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Mood matches (happy) +1.0
  - Energy closeness 0.98 (+2.94)
  - Valence closeness 0.96 (+1.92)
  - Danceability closeness 0.99 (+1.98)
  - Acousticness closeness 0.98 (+1.96)
==================================================
2. Gym Hero — Score: 10.09
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.87 (+2.61)
  - Valence closeness 0.97 (+1.94)
  - Danceability closeness 0.92 (+1.84)
  - Acousticness closeness 0.85 (+1.70)
==================================================
3. Rooftop Lights — Score: 9.52
--------------------------------------------------
  - Mood matches (happy) +1.0
  - Energy closeness 0.96 (+2.88)
  - Valence closeness 0.99 (+1.98)
  - Danceability closeness 0.98 (+1.96)
  - Acousticness closeness 0.85 (+1.70)
==================================================
4. Fire In The Sky — Score: 8.78
--------------------------------------------------
  - Energy closeness 0.98 (+2.94)
  - Valence closeness 0.92 (+1.84)
  - Danceability closeness 1.00 (+2.00)
  - Acousticness closeness 1.00 (+2.00)
==================================================
5. Night Drive Loop — Score: 8.05
--------------------------------------------------
  - Energy closeness 0.95 (+2.85)
  - Valence closeness 0.69 (+1.38)
  - Danceability closeness 0.93 (+1.86)
  - Acousticness closeness 0.98 (+1.96)
==================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Adversarial / Edge Case Testing

To stress-test the scoring logic, we ran `recommend_songs` against several deliberately tricky user profiles — contradictory preferences, missing fields, out-of-range values, and typos. This surfaced two real bugs, which we then fixed in `score_song`. These same 8 profiles are now also formalized as automated regression tests in `tests/test_agent.py`, so they're checked on every run instead of by eyeballing printed output.

**Heads up:** the raw outputs below were captured before the agent existed, straight from `recommend_songs`. Running these same profiles through `src/agent.py` today gives different numbers for Profile 4 and Profile 5 specifically, since the agent now normalizes casing and clamps out of range values before scoring, rather than after. The scoring logic itself hasn't changed, just when the cleanup happens.

1. **`likes_acoustic` was dead code.** The field was parsed into every profile but never read anywhere in the scoring formula. Fixed by adding a +1.0 bonus when `likes_acoustic` is `True` and the song's `acousticness >= 0.5`.
2. **Out-of-range preference values produced negative scores.** Feature closeness (`1 - |song value - user preference|`) assumed both values were in `[0, 1]`; a preference like `energy=1.8` could push closeness — and therefore points — negative. Fixed by clamping closeness to `max(0.0, ...)`.

The outputs below are from `recommend_songs`, using the fixed scoring logic.

### 1. Conflicted (high energy but "sad" mood)
prefs: `{'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.9, 'danceability': 0.8, 'acousticness': 0.1, 'likes_acoustic': False}`

```
Top recommendations:
==================================================
1. Sunrise City — Score: 10.46
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.92 (+2.76)
  - Valence closeness 0.94 (+1.88)
  - Danceability closeness 0.99 (+1.98)
  - Acousticness closeness 0.92 (+1.84)
==================================================
2. Gym Hero — Score: 10.39
--------------------------------------------------
  - Genre matches (pop) +2.0
  - Energy closeness 0.97 (+2.91)
  - Valence closeness 0.87 (+1.74)
  - Danceability closeness 0.92 (+1.84)
  - Acousticness closeness 0.95 (+1.90)
==================================================
3. Neon Pulse Rave — Score: 8.35
--------------------------------------------------
  - Energy closeness 0.93 (+2.79)
  - Valence closeness 0.98 (+1.96)
  - Danceability closeness 0.88 (+1.76)
  - Acousticness closeness 0.92 (+1.84)
==================================================
4. Fire In The Sky — Score: 8.08
--------------------------------------------------
  - Energy closeness 0.88 (+2.64)
  - Valence closeness 0.82 (+1.64)
  - Danceability closeness 1.00 (+2.00)
  - Acousticness closeness 0.90 (+1.80)
==================================================
5. Rooftop Lights — Score: 7.86
--------------------------------------------------
  - Energy closeness 0.86 (+2.58)
  - Valence closeness 0.91 (+1.82)
  - Danceability closeness 0.98 (+1.96)
  - Acousticness closeness 0.75 (+1.50)
==================================================
```
**Finding:** the #1 result, *Sunrise City*, is mood=`happy`, not `sad`. Strong energy/valence/danceability closeness outweighs a single 1-point mood mismatch — a "sad" listener gets happy pop songs.

### 2. `likes_acoustic` contradiction (says "I like acoustic" but sets acousticness target to 0.0)
prefs: `{'genre': 'lofi', 'mood': 'chill', 'acousticness': 0.0, 'likes_acoustic': True}`

```
Top recommendations:
==================================================
1. Midnight Coding — Score: 4.58
--------------------------------------------------
  - Genre matches (lofi) +2.0
  - Mood matches (chill) +1.0
  - Acousticness closeness 0.29 (+0.58)
  - Likes acoustic music and song is acoustic (+1.00)
==================================================
2. Library Rain — Score: 4.28
--------------------------------------------------
  - Genre matches (lofi) +2.0
  - Mood matches (chill) +1.0
  - Acousticness closeness 0.14 (+0.28)
  - Likes acoustic music and song is acoustic (+1.00)
==================================================
3. Focus Flow — Score: 3.44
--------------------------------------------------
  - Genre matches (lofi) +2.0
  - Acousticness closeness 0.22 (+0.44)
  - Likes acoustic music and song is acoustic (+1.00)
==================================================
4. Spacewalk Thoughts — Score: 2.16
--------------------------------------------------
  - Mood matches (chill) +1.0
  - Acousticness closeness 0.08 (+0.16)
  - Likes acoustic music and song is acoustic (+1.00)
==================================================
5. Neon Pulse Rave — Score: 1.96
--------------------------------------------------
  - Acousticness closeness 0.98 (+1.96)
==================================================
```
**Finding:** after the fix, `likes_acoustic` now visibly contributes a "+1.00" bonus line for acoustic songs — confirming the flag is finally wired into scoring.

### 3. Empty profile
prefs: `{}`

```
Top recommendations:
==================================================
1. Sunrise City — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
2. Midnight Coding — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
3. Storm Runner — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
4. Library Rain — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
5. Gym Hero — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
```
**Finding:** every song ties at 0.0, and the top 5 returned exactly match the CSV's row order (a stable sort). An empty profile isn't "no preference" — it silently degrades into "return the first 5 rows of the file."

### 4. Case-sensitivity typo
prefs: `{'genre': 'Pop', 'mood': 'Happy', 'energy': 0.8}`

```
Top recommendations:
==================================================
1. Sunrise City — Score: 2.94
--------------------------------------------------
  - Energy closeness 0.98 (+2.94)
==================================================
2. Fire In The Sky — Score: 2.94
--------------------------------------------------
  - Energy closeness 0.98 (+2.94)
==================================================
3. Rooftop Lights — Score: 2.88
--------------------------------------------------
  - Energy closeness 0.96 (+2.88)
==================================================
4. Night Drive Loop — Score: 2.85
--------------------------------------------------
  - Energy closeness 0.95 (+2.85)
==================================================
5. Concrete Throne — Score: 2.70
--------------------------------------------------
  - Energy closeness 0.90 (+2.70)
==================================================
```
**Finding:** *Sunrise City* is an exact `pop`/`happy` match, but `"Pop" != "pop"` in Python, so it ties for 1st with an unrelated funk song instead of winning outright on genre + mood.

### 5. Out-of-range values
prefs: `{'energy': 1.8, 'valence': -0.5}`

```
Top recommendations:
==================================================
1. Iron Collapse — Score: 0.75
--------------------------------------------------
  - Energy closeness 0.15 (+0.45)
  - Valence closeness 0.15 (+0.30)
==================================================
2. Neon Pulse Rave — Score: 0.51
--------------------------------------------------
  - Energy closeness 0.17 (+0.51)
  - Valence closeness 0.00 (+0.00)
==================================================
3. Faded Photographs — Score: 0.40
--------------------------------------------------
  - Energy closeness 0.00 (+0.00)
  - Valence closeness 0.20 (+0.40)
==================================================
4. Gym Hero — Score: 0.39
--------------------------------------------------
  - Energy closeness 0.13 (+0.39)
  - Valence closeness 0.00 (+0.00)
==================================================
5. Storm Runner — Score: 0.37
--------------------------------------------------
  - Energy closeness 0.11 (+0.33)
  - Valence closeness 0.02 (+0.04)
==================================================
```
**Finding:** before the fix, several of these scores were negative (down to -0.25). After clamping closeness to `max(0.0, ...)`, the worst case is now 0.00 instead of going negative.

### 6. Single-feature profile
prefs: `{'energy': 0.5}`

```
Top recommendations:
==================================================
1. Dusty Backroads — Score: 3.00
--------------------------------------------------
  - Energy closeness 1.00 (+3.00)
==================================================
2. surf. — Score: 2.85
--------------------------------------------------
  - Energy closeness 0.95 (+2.85)
==================================================
3. Velvet Hours — Score: 2.85
--------------------------------------------------
  - Energy closeness 0.95 (+2.85)
==================================================
4. Midnight Coding — Score: 2.76
--------------------------------------------------
  - Energy closeness 0.92 (+2.76)
==================================================
5. Focus Flow — Score: 2.70
--------------------------------------------------
  - Energy closeness 0.90 (+2.70)
==================================================
```
**Finding:** behaves reasonably — ranks purely by energy closeness. Unset features are fully ignored (not penalized), which is expected but worth documenting explicitly.

### 7. Unknown/extra key (`tempo_bpm`)
prefs: `{'genre': 'rock', 'tempo_bpm': 140}`

```
Top recommendations:
==================================================
1. Storm Runner — Score: 2.00
--------------------------------------------------
  - Genre matches (rock) +2.0
==================================================
2. Sunrise City — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
3. Midnight Coding — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
4. Library Rain — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
5. Gym Hero — Score: 0.00
--------------------------------------------------
  - (no scoring criteria applied to this song)
==================================================
```
**Finding:** `tempo_bpm` is silently ignored — `Song` has that field, but `FEATURE_MAX_POINTS` doesn't, so a user's tempo preference has zero effect on the outcome with no warning.

### 8. Perfect opposite (all-zero features, nonexistent genre/mood)
prefs: `{'genre': 'none-existing-genre', 'mood': 'none-existing-mood', 'energy': 0.0, 'valence': 0.0, 'danceability': 0.0, 'acousticness': 0.0}`

```
Top recommendations:
==================================================
1. Faded Photographs — Score: 5.35
--------------------------------------------------
  - Energy closeness 0.75 (+2.25)
  - Valence closeness 0.70 (+1.40)
  - Danceability closeness 0.75 (+1.50)
  - Acousticness closeness 0.10 (+0.20)
==================================================
2. Quiet Reverie — Score: 5.06
--------------------------------------------------
  - Energy closeness 0.80 (+2.40)
  - Valence closeness 0.45 (+0.90)
  - Danceability closeness 0.85 (+1.70)
  - Acousticness closeness 0.03 (+0.06)
==================================================
3. Velvet Hours — Score: 4.95
--------------------------------------------------
  - Energy closeness 0.55 (+1.65)
  - Valence closeness 0.50 (+1.00)
  - Danceability closeness 0.45 (+0.90)
  - Acousticness closeness 0.70 (+1.40)
==================================================
4. Iron Collapse — Score: 4.49
--------------------------------------------------
  - Energy closeness 0.05 (+0.15)
  - Valence closeness 0.65 (+1.30)
  - Danceability closeness 0.55 (+1.10)
  - Acousticness closeness 0.97 (+1.94)
==================================================
5. surf. — Score: 4.35
--------------------------------------------------
  - Energy closeness 0.55 (+1.65)
  - Valence closeness 0.38 (+0.76)
  - Danceability closeness 0.52 (+1.04)
  - Acousticness closeness 0.45 (+0.90)
==================================================
```
**Finding:** even with genre/mood matching nothing, feature closeness alone lands a song at 5.35 out of a possible 12 points — the score floor from numeric closeness is higher than it might intuitively seem.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

**We temporarily removed the mood check entirely and reran our 8 test profiles; only one profile's ranking actually changed, showing mood is a fairly weak signal in this dataset since most songs never had a matching mood to begin with.**

**We also doubled energy's weight (3.0 to 6.0) and halved genre's (2.0 to 1.0), which flipped the #1 result from Sunrise City to Gym Hero for one profile, proving the ranking is sensitive to small weight choices and not just to what the user actually asked for.**

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



