# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.



---

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

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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



