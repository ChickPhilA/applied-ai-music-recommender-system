"""
Agentic workflow layer for the recommender: plan -> act -> check its own work.

Wraps the existing scoring engine (recommender.py) with:
  1. Normalize  - fix known input quirks (casing, out-of-range values) before scoring
  2. Detect     - flag known problem patterns in the profile without blocking on them
  3. Act        - call the existing recommend_songs() unchanged
  4. Check      - self-critique each result with a confidence label

See README.md's "Agentic Loop & Confidence Scoring" section for the rationale.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .recommender import FEATURE_MAX_POINTS, recommend_songs

RECOGNIZED_KEYS = {"genre", "mood", "likes_acoustic"} | set(FEATURE_MAX_POINTS.keys())
NUMERIC_KEYS = set(FEATURE_MAX_POINTS.keys())

CONTRADICTION_LOW_ACOUSTICNESS = 0.3
CONTRADICTION_HIGH_ACOUSTICNESS = 0.7

LOW_COVERAGE_THRESHOLD = 0.3
LOW_MARGIN_THRESHOLD = 0.5
HIGH_COVERAGE_THRESHOLD = 0.6
HIGH_MARGIN_THRESHOLD = 1.0


@dataclass
class AgentResult:
    recommendations: List[Tuple[Dict, float, str, str]]
    log: List[Dict[str, str]] = field(default_factory=list)


def _normalize(raw_prefs: Dict) -> Tuple[Dict, List[Dict[str, str]]]:
    """Lowercases genre/mood and clamps numeric prefs into [0, 1]. Logs any change."""
    prefs = dict(raw_prefs)
    log = []

    for key in ("genre", "mood"):
        if isinstance(prefs.get(key), str):
            normalized = prefs[key].strip().lower()
            if normalized != prefs[key]:
                log.append({
                    "step": "normalize",
                    "detail": f"Normalized casing on '{key}': {prefs[key]!r} -> {normalized!r}",
                })
            prefs[key] = normalized

    for key in NUMERIC_KEYS:
        if key in prefs:
            clamped = max(0.0, min(1.0, prefs[key]))
            if clamped != prefs[key]:
                log.append({
                    "step": "normalize",
                    "detail": f"Clamped out-of-range preference '{key}': {prefs[key]} -> {clamped}",
                })
            prefs[key] = clamped

    return prefs, log


def _detect_issues(prefs: Dict) -> List[Dict[str, str]]:
    """Flags known problem patterns without blocking on them."""
    log = []

    if not any(key in prefs for key in RECOGNIZED_KEYS):
        log.append({
            "step": "detect",
            "detail": "Profile is empty (no recognized preference keys) — "
                      "recommendations will be undifferentiated and confidence forced low.",
        })

    if "likes_acoustic" in prefs and "acousticness" in prefs:
        likes_acoustic = prefs["likes_acoustic"]
        acousticness = prefs["acousticness"]
        if likes_acoustic and acousticness < CONTRADICTION_LOW_ACOUSTICNESS:
            log.append({
                "step": "detect",
                "detail": f"Contradiction: likes_acoustic=True but acousticness target is "
                          f"{acousticness} (low). Scoring both signals as given.",
            })
        elif not likes_acoustic and acousticness >= CONTRADICTION_HIGH_ACOUSTICNESS:
            log.append({
                "step": "detect",
                "detail": f"Contradiction: likes_acoustic=False but acousticness target is "
                          f"{acousticness} (high). Scoring both signals as given.",
            })

    unsupported = sorted(set(prefs) - RECOGNIZED_KEYS)
    if unsupported:
        log.append({
            "step": "detect",
            "detail": f"Ignoring unsupported preference key(s): {', '.join(unsupported)} — not currently scored.",
        })

    return log


def compute_confidence(coverage: float, margin: float) -> str:
    """Labels how much a recommendation's rank should be trusted."""
    if coverage < LOW_COVERAGE_THRESHOLD:
        return "low"
    if margin < LOW_MARGIN_THRESHOLD:
        return "low"
    if coverage >= HIGH_COVERAGE_THRESHOLD and margin >= HIGH_MARGIN_THRESHOLD:
        return "high"
    return "medium"


def plan_and_recommend(raw_prefs: Dict, songs: List[Dict], k: int = 5) -> AgentResult:
    """Plan (normalize + detect) -> act (score & rank) -> check (self-critique) loop."""
    prefs, normalize_log = _normalize(raw_prefs)
    detect_log = _detect_issues(prefs)
    log = normalize_log + detect_log

    ranked = recommend_songs(prefs, songs, k=k)
    coverage = len(set(prefs) & RECOGNIZED_KEYS) / len(RECOGNIZED_KEYS)

    scores = [score for _, score, _ in ranked]
    recommendations = []
    for i, (song, score, explanation) in enumerate(ranked):
        if len(scores) == 1:
            margin = score
        elif i + 1 < len(scores):
            margin = score - scores[i + 1]
        else:
            margin = score - scores[i - 1]
        confidence = compute_confidence(coverage, margin)
        recommendations.append((song, score, explanation, confidence))

    if recommendations and recommendations[0][3] == "low":
        log.append({
            "step": "check",
            "detail": f"Self-critique: top pick '{recommendations[0][0]['title']}' "
                      f"has low confidence — treat this ranking with caution.",
        })

    return AgentResult(recommendations=recommendations, log=log)
