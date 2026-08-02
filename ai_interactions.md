# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to help extend my Project 3 recommender into a final project applied AI system by adding an Agentic Workflow, since the final project requires at least one AI feature and that category (plan, act, and check its own work) fit my project best. We agreed on a deterministic Python loop instead of live LLM calls so it would realistically get done by the deadline, and we treated the self critique / confidence step as the main event, since that's the part that actually makes it agentic instead of just a cleaner scorer.

**Prompts used:**

- "Give me recommendations for the extension track, simple and short explanations of each one and what they do, as well as which one you think could apply to my project the best."
- "What if I just did testing plus confidence scoring?"
- "This is due tomorrow (Sunday) night. I think we can flesh out the agentic loop plus logging and the testing plus confidence scoring."
- After finding the official requirements only asked for one AI feature, I asked the agent to reframe the work as a single Agentic Workflow feature, with confidence scoring folded in as the "check" step rather than treated as a second, separate feature.

**What did the agent generate or change?**

- `src/agent.py` (new): `plan_and_recommend()` normalizes input casing and value ranges, detects known problem patterns (empty profile, a `likes_acoustic` contradiction, unsupported keys like `tempo_bpm`), calls the existing `recommend_songs()` without changing it, then self critiques each result with a `compute_confidence()` label (low, medium, or high) based on how much of the profile was actually specified and how close the score is to the next ranked song.
- `src/main.py`: swapped the direct `recommend_songs()` calls for `plan_and_recommend()`, and updated `print_recommendations()` to print the agent's log trail and each song's confidence label.
- `tests/test_agent.py` (new): 12 automated tests. Four check `compute_confidence` directly, and the rest formalize each of the 8 adversarial profiles that I had previously only checked by eyeballing printed output.
- Set up a local `.venv` and installed `requirements.txt` so `pytest` could actually run, since neither existed yet.

**What did you verify or fix manually?**

- Ran `python -m src.main` and confirmed the default profile's top pick comes back as high confidence (a genuine match, no issues), while Adversarial Profile 1 (conflicted pop/sad) gets flagged as low confidence on its mismatched top pick. That's the same bug I found by hand in Project 3, now caught automatically. Profile 2's `likes_acoustic` contradiction and Profile 3's empty profile case both showed up in the log as expected.
- Ran the full test suite with `python -m pytest` and confirmed all 12 new agent tests pass, and the 3 original dict based `score_song` tests still pass untouched. Two pre-existing failures in the unused `Recommender` / `UserProfile` class stub showed up too, but those predate this work and are unrelated to the agent loop, so I left them alone.
- Double checked that `recommender.py` itself was never modified. The agent wraps the existing scoring engine instead of duplicating or changing it.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
