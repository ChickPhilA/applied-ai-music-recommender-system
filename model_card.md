# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Model name: **Harmo-Vibe: Agentic Music Recommender**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

**Our recomemnder is made for hardcore or ameteaur music enjoyers alike, to find the best song recommendations based on the user's personal preferences.**

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

**We first measure with the features of each song. These features include genre and mood (categoies), energy, valence, danceability, and acousticness (0 to 1 scale in terms of closeness), and also the song's tempo's BPM (but that's actually not really used in the scoring).**

**These features are measured against the user's preferences. We see if the user's genre and mood matches with the song (bonus points in the scoring process), target values for energy, valence, danceability, and acousticness are close to the song's initial feature values, and a yes/no flag for liking acoustic music.**

**The user's preferences to the song's features are measured to a score by the following grading standards:**
- **Genre match = flat bonus points**
- **Mood match = flat bonus points (smaller than genre, however)**
- **Each numeric feature = points based on how close the song's value is to the user's target, rather than being the same, precise score**
- **Acoustic-lover flag = small bonus is the song is acoustic enough**

**Comparing to the initial starter logic, a few bugs were found and fixed:**
- **The acoustic-lover flag was being collected but actually never used**
- **Target values outside the normal 0-1 range could make a song's sore go negative**




---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

**There are 20 songs in the catalog. 17 different genres are represented, but most appear only once. 16 different moods are represented, with chill and happy/intense being the only repeats.**

**No data was added or removed as we used the start CSV as it was.**

**In the dataset, lyrics, instrumentation/vocals, cultural context, and tempo preference weren't scored even though the data has it. Energy values also cluster unevenly (which there is a noticable gap between 0.5 and 0.7), so "moderate energy" tastes are underserved.**

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

**Our recommender handles profiles with consistent, clear, in-range preferences well. For example, the default "happy pop" profile", or the single-feature energy = 0.5 profile, since both got clean, sensible top picks with no bugs nor bias distortion, and fair scaling.**

**Genre and mood matching works exactly as intended when the same string is being used between the song and the user's preferences. Numeric closeness scoring correctly rewards songs that are near the target and penalizes ones that are far off.**

**Sunrise City winning for a happy/pop/high-energy profile made sense, since the song's real vlaues genuinely fit that description. Dusty Backroads winning for an energy=0.5 only profile also made sense, since it has energy exactly 0.5.**

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

**A weakness that was discovered during our experiments was heavily weighing bias towards energy, while shifting away from genre as a factor in our recommendation algorithm. Energy's weight in deciding which songs to recommend from our .csv file was already a multipler of 3.0, which already gives the feature a major bias over other songs' features. However, when we doubled the weight multiplier by 2, our energy's weight totaled to 6.0, which halving genre's weight (initially 2.0) to 1.0. This caused user profiles' who have low energy preferences but in favor of genre(s) in general, to be provided unrealisitc recommendations from our .csv file.**

**In the experiment, a profile, initially having Sunrise City as its top recommendation, was flipped with Gym Hero in its rankings, showing that the ranking is sensitive to small weight choices, not just to what the user is actually asking for.**

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

**We tested 8 profiles in general. These were the qualities of the profiles and their results:**

**Profile 1: Conflicted (pop/sad, high energy preference)** --> Sunrise City (a happy song) win; mood mismatch outweighted by energy/valence match. Bias towards energy scoring here

**Profile 2: likes_acoustic contradiction** --> Midnight Coding wins, despite user's acousticness value of 0.0, but prefers to like acoustic music. Midnight Coding has a low closeness acoustic store, but still recommended after likes_acoustic scoring bug was fixed.

**Profile 3: Empty file: no data at all** --> All songs tie at 0.00. Returns CSV file order.

**Profile 4: Case Type ("Pop", "Happy")** --> Sunrise City ties for #1 despite exact match, loses genre/mood points to capitalization in profile data.

**Profile 5: Out-of-range values (energy=1.8)** --> Iron Collapse wins with score of 0.75. No negative scores after clamp fix.

**Profile 6: Single-feature (energy=0.5 ONLY)** --> Dusty Backroads wins- ranks purely for energy closeness.

**Profile 7: Unknown key (tempo_bpm)** --> Storm Runner wins on genre alone; tempo feature was silently ignored.

**Profile 8: Perfect opposite (all zeroes, fake genre/mood)** --> Faded Photographs win at 5.35; feature closeness alone gave a fairly high floor.

No need for numeric metrics unless you created some.

**Profile comparisons:**

Profiles 1 vs 2: Profile 1 (pop/sad, high energy) lets energy and valence overpower a mood mismatch, while Profile 2 (lofi/chill, contradicts acousticness) wins mainly on genre+mood match, showing energy dominates when it's strong, but genre+mood dominate when energy isn't in play.

Profiles 3 vs 4: Profile 3 (empty) has nothing to score against so it just returns file order, while Profile 4 (case typo) actually scores on energy alone because the capitalized genre/mood strings silently fail to match, proving exact-string matching is case-sensitive and unforgiving.

Profiles 5 vs 6: Profile 5 (out-of-range energy) shows the formula can produce invalid negative points without a clamp, while Profile 6 (a single valid feature) shows the same formula behaves perfectly reasonably when given in-range input, meaning the bug was about bad input, not bad math.

Profiles 7 vs 8: Profile 7 (unknown tempo_bpm key) shows unsupported preferences are silently ignored with zero effect, while Profile 8 (all-zero, fake genre/mood) shows that even a "worst case" profile still scores respectably high from feature closeness alone, meaning the score floor is higher than it feels like it should be.

**Since these 8 profiles were originally checked by hand, we later built an agentic loop (`src/agent.py`) that automates this same evaluation on every run.** It normalizes inputs, detects the same problem patterns we found manually (empty profiles, contradictory flags, unsupported keys), and self critiques its own top pick with a confidence label. Profile 1's mood mismatch, which used to require us noticing it in printed output, now gets flagged automatically as low confidence. All 8 profiles are also locked in as automated tests in `tests/test_agent.py`, so this evaluation is no longer a one-time manual pass.

**Testing summary, pulled from an actual run:**

- `pytest` results: 15 passed, 2 failed
- All 12 agent tests pass
- The 2 failures are the pre-existing, out-of-scope OOP stub, unrelated to this work
- Across the 8 adversarial profiles plus the default profile, 45 total ranked recommendations were produced
- Confidence label breakdown: 2 high, 8 medium, 35 low
- The heavy lean toward low confidence is expected and correct, since the adversarial profiles are deliberately sparse, contradictory, or extreme, so the agent is properly flagging exactly the situations it should be cautious about

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

**If I were to improve the model in the future, the first thing that I would add are more features to be measured in order to add more variety and scaling in weighing out the scoring further. For instance, if I were to add other features such as vocals, lyrics, instrumentation, loudness, etc., our scaling would add more precision to the recommendation score. In fact, lyrics and instrumentation were features missing mentioned earlier, in Section 4 of this Model Card.**

**To better explain recommendations, we could show users how confident a match actually is, rather than it just being a point breakdown, so they can know if it's a great fit or just the least-bad option.**

**Adding some intentional variety would mix up the variety instead of always returning the same strict top-k, and handling mixed/contradictiory preferences without letting one strong feature silently override the rest.**

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

**My biggest learning moment about recommender systems is that we can use a mathematical algorithm using an average target value (being the centroid) by just proximity, rather than being a precise-exact value. This helped me understand better how music recommenders on Spotify, YouTube, or other streaming platforms help gather the best recommendations for user's based on their personal preferences or activities.**

**In the future, I could add other features as mentioned prior in the model card to better tailor the user's personal preferences, such as cultural/other languages, to see how other types of music could be measured with our current algorithm. There are over 150 million songs in history; no matter how historically significant or culturally recent it may be, all music can fit one music recommender, for many people.**

---

## 10. Reflection and Ethics (Final Project)

### What are the limitations or biases in your system?

My agent is not actually intelligent. It is just a series of if and else checks, not a trained model, so it can only catch the exact problems I thought to look for. The catalog is still only 20 songs, so it can never really generalize past what is in that one CSV file. The confidence labels come from thresholds I picked myself, like 0.3 for coverage and 0.5 for margin, and those were not tested against real data, just my own judgment. There is also a small bug where the last ranked song in a list gets compared to the wrong neighbor, which makes it look low confidence even when that might not be the real reason. On top of that, the original bias from Project 3 is still there too, genre matching is weighted heavily, so it can crowd out a song that is actually a closer overall match.

### Could your AI be misused, and how would you prevent that?

The biggest risk is someone trusting a high confidence label as some kind of guarantee instead of what it actually is, a rough signal based on score margin and how complete the profile was. Since everything is deterministic and rule based, there is not really a security risk like there would be with a live model that could be tricked or manipulated. To prevent the confidence being misread, I tried to be clear in the README and model card that this is a rule based system with hand picked thresholds, not a trained model, and I made sure the agent logs what it is doing so nothing is hidden.

### What surprised you while testing your AI's reliability?

The thing that actually surprised me was realizing that running the same 8 adversarial profiles through the new agent changed two of the results compared to before. Profile 4 and Profile 5 came out differently, not because the scoring math changed, but because the agent now cleans up the input before scoring instead of after. I also expected the confidence labels to be more balanced, but 35 out of 45 recommendations came back low confidence. At first that looked like a bug, but it actually made sense once I realized those profiles were built on purpose to be messy or contradictory.

### Describe your collaboration with AI during this project

One genuinely helpful moment was when I realized "agentic loop plus testing" was actually two separate items from the requirements, and the AI helped me fold confidence scoring into the agentic loop as its own check step instead of building two separate things. One flawed moment was that small bug with the last ranked song being compared to the wrong neighbor, it slipped through until we actually looked closely at real output together. The first draft of a few commit messages was also way too long and had to be shortened after I pushed back on it.

