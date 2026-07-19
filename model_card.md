# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
