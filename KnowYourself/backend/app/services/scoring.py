"""KnowYourself — Scoring algorithms for all assessments.

Big Five: IPIP-NEO-PI 50-item short form scoring.
Archetype: 12 Jungian brand archetypes from 24 forced-choice questions.
Consciousness: Hawkins Map of Consciousness from 10 Likert items.
"""

# ============================================================
# BIG FIVE (IPIP 50-item)
# ============================================================
# Each trait has 10 items. Items are scored 1-5.
# Some items are reverse-keyed (R).
# The 50 IPIP items map to traits in this order (1-indexed):
#   Extraversion:       1, 6R, 11, 16R, 21, 26R, 31, 36R, 41, 46R
#   Agreeableness:      2R, 7, 12R, 17, 22R, 27, 32R, 37, 42R, 47
#   Conscientiousness:  3, 8R, 13, 18R, 23, 28R, 33, 38R, 43, 48R
#   Neuroticism:        4, 9R, 14, 19R, 24, 29R, 34, 39R, 44, 49R
#   Openness:           5, 10R, 15, 20R, 25, 30R, 35, 40R, 45, 50R

BIG_FIVE_KEYS = {
    "extraversion": {
        "items": [0, 5, 10, 15, 20, 25, 30, 35, 40, 45],
        "reverse": [5, 15, 25, 35, 45],
    },
    "agreeableness": {
        "items": [1, 6, 11, 16, 21, 26, 31, 36, 41, 46],
        "reverse": [1, 11, 21, 31, 41],
    },
    "conscientiousness": {
        "items": [2, 7, 12, 17, 22, 27, 32, 37, 42, 47],
        "reverse": [7, 17, 27, 37, 47],
    },
    "neuroticism": {
        "items": [3, 8, 13, 18, 23, 28, 33, 38, 43, 48],
        "reverse": [8, 18, 28, 38, 48],
    },
    "openness": {
        "items": [4, 9, 14, 19, 24, 29, 34, 39, 44, 49],
        "reverse": [9, 19, 29, 39, 49],
    },
}


def score_big_five(answers: list[int]) -> dict[str, float]:
    """Score 50 IPIP items into Big Five traits (0-100 scale)."""
    if len(answers) != 50:
        raise ValueError(f"Expected 50 answers, got {len(answers)}")

    scores = {}
    for trait, keys in BIG_FIVE_KEYS.items():
        total = 0
        for idx in keys["items"]:
            val = answers[idx]
            if idx in keys["reverse"]:
                val = 6 - val  # reverse: 1->5, 2->4, 3->3, 4->2, 5->1
            total += val
        # 10 items, each 1-5, so range is 10-50. Normalise to 0-100.
        scores[trait] = round((total - 10) / 40 * 100, 1)

    return scores


# ============================================================
# JUNGIAN ARCHETYPES (24 forced-choice)
# ============================================================
# 12 archetypes, each tested by 2 questions.
# Each question pits two archetypes against each other (A vs B).

ARCHETYPES = [
    "Hero", "Sage", "Explorer", "Outlaw", "Magician", "Lover",
    "Jester", "Caregiver", "Ruler", "Creator", "Innocent", "Regular Person",
]

# 24 questions: (archetype_for_A, archetype_for_B)
ARCHETYPE_PAIRS = [
    ("Hero", "Caregiver"),
    ("Sage", "Jester"),
    ("Explorer", "Ruler"),
    ("Outlaw", "Innocent"),
    ("Magician", "Regular Person"),
    ("Lover", "Creator"),
    ("Hero", "Sage"),
    ("Explorer", "Outlaw"),
    ("Magician", "Lover"),
    ("Jester", "Caregiver"),
    ("Ruler", "Creator"),
    ("Innocent", "Regular Person"),
    ("Hero", "Explorer"),
    ("Sage", "Magician"),
    ("Outlaw", "Jester"),
    ("Lover", "Caregiver"),
    ("Ruler", "Innocent"),
    ("Creator", "Regular Person"),
    ("Hero", "Outlaw"),
    ("Sage", "Lover"),
    ("Explorer", "Magician"),
    ("Jester", "Ruler"),
    ("Caregiver", "Creator"),
    ("Innocent", "Regular Person"),
]


def score_archetype(answers: list[str]) -> dict:
    """Score 24 forced-choice items into archetype percentages."""
    if len(answers) != 24:
        raise ValueError(f"Expected 24 answers, got {len(answers)}")

    tallies = {a: 0 for a in ARCHETYPES}
    for i, choice in enumerate(answers):
        a_type, b_type = ARCHETYPE_PAIRS[i]
        if choice.upper() == "A":
            tallies[a_type] += 1
        else:
            tallies[b_type] += 1

    total = sum(tallies.values())
    percentages = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in tallies.items()}

    sorted_types = sorted(tallies.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_types[0][0]
    shadow = sorted_types[-1][0]

    return {
        "primary_archetype": primary,
        "shadow_archetype": shadow,
        "percentages": percentages,
    }


# ============================================================
# HAWKINS CONSCIOUSNESS SCALE (10 items)
# ============================================================
# 10 questions, each 1-5 Likert. Maps to consciousness levels.
# Average score maps to a level on the Hawkins scale.

HAWKINS_LEVELS = [
    (20, "Shame"),
    (30, "Guilt"),
    (50, "Apathy"),
    (75, "Grief"),
    (100, "Fear"),
    (125, "Desire"),
    (150, "Anger"),
    (175, "Pride"),
    (200, "Courage"),
    (250, "Neutrality"),
    (310, "Willingness"),
    (350, "Acceptance"),
    (400, "Reason"),
    (500, "Love"),
    (540, "Joy"),
    (600, "Peace"),
    (700, "Enlightenment"),
]


def score_consciousness(answers: list[int]) -> dict:
    """Score 10 Likert items into a Hawkins consciousness level."""
    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")

    avg = sum(answers) / len(answers)  # 1.0 to 5.0
    # Map 1-5 average to 20-600 consciousness scale
    level = int(20 + (avg - 1) / 4 * 580)

    # Find the named level
    level_name = "Shame"
    for threshold, name in HAWKINS_LEVELS:
        if level >= threshold:
            level_name = name
        else:
            break

    return {"level": level, "level_name": level_name}
