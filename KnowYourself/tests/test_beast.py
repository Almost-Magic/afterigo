"""KnowYourself — Beast Test Suite.

Section 1: Imports & Configuration
Section 2: Unit Tests (scoring algorithms)
Section 3: Integration Tests (database)
Section 4: API Smoke Tests
Section 5: Confidence Stamp
"""

import asyncio
import os
import sys
import uuid

# ============================================================
# SECTION 1 — IMPORTS & CONFIGURATION
# ============================================================

os.environ["KNOWYOURSELF_TESTING"] = "1"

import httpx
import pytest

# Direct imports for unit tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.scoring import (
    ARCHETYPES,
    ARCHETYPE_PAIRS,
    BIG_FIVE_KEYS,
    HAWKINS_LEVELS,
    score_archetype,
    score_big_five,
    score_consciousness,
)

API_BASE = os.environ.get("KNOWYOURSELF_API", "http://localhost:8300")
_RUN_ID = uuid.uuid4().hex[:8]

passed = []
failed = []


def record(name: str, ok: bool, detail: str = ""):
    if ok:
        passed.append(name)
        print(f"  PASS  {name}")
    else:
        failed.append(name)
        print(f"  FAIL  {name} -- {detail}")


# ============================================================
# SECTION 2 — UNIT TESTS (scoring algorithms)
# ============================================================

def test_big_five_all_threes():
    """All neutral (3) should give 50% for all traits."""
    answers = [3] * 50
    scores = score_big_five(answers)
    for trait, val in scores.items():
        record(f"bf_neutral_{trait}", val == 50.0, f"expected 50.0, got {val}")


def test_big_five_extreme_high():
    """All 5s should give high scores (accounting for reverse items)."""
    answers = [5] * 50
    scores = score_big_five(answers)
    for trait, val in scores.items():
        # With all 5s: normal items=5, reverse items=6-5=1
        # 5 normal + 5 reverse = 5*5 + 5*1 = 30, normalised = (30-10)/40*100 = 50
        record(f"bf_high_{trait}", val == 50.0, f"expected 50.0, got {val}")


def test_big_five_max_extraversion():
    """Max extraversion: normal items=5, reverse items=1."""
    answers = [3] * 50
    for idx in BIG_FIVE_KEYS["extraversion"]["items"]:
        if idx in BIG_FIVE_KEYS["extraversion"]["reverse"]:
            answers[idx] = 1  # reverse: 6-1=5
        else:
            answers[idx] = 5  # normal: 5
    scores = score_big_five(answers)
    record("bf_max_extraversion", scores["extraversion"] == 100.0, f"got {scores['extraversion']}")


def test_big_five_min_extraversion():
    """Min extraversion: normal items=1, reverse items=5."""
    answers = [3] * 50
    for idx in BIG_FIVE_KEYS["extraversion"]["items"]:
        if idx in BIG_FIVE_KEYS["extraversion"]["reverse"]:
            answers[idx] = 5  # reverse: 6-5=1
        else:
            answers[idx] = 1  # normal: 1
    scores = score_big_five(answers)
    record("bf_min_extraversion", scores["extraversion"] == 0.0, f"got {scores['extraversion']}")


def test_big_five_wrong_count():
    """Wrong number of answers should raise."""
    try:
        score_big_five([3] * 49)
        record("bf_wrong_count", False, "should have raised ValueError")
    except ValueError:
        record("bf_wrong_count", True)


def test_archetype_all_a():
    """All A choices should produce valid archetypes."""
    answers = ["a"] * 24
    result = score_archetype(answers)
    record("arch_all_a_primary", result["primary_archetype"] in ARCHETYPES, f"got {result['primary_archetype']}")
    record("arch_all_a_shadow", result["shadow_archetype"] in ARCHETYPES, f"got {result['shadow_archetype']}")
    record("arch_all_a_pct_sum", abs(sum(result["percentages"].values()) - 100.0) < 1.0,
           f"pct sum = {sum(result['percentages'].values())}")


def test_archetype_all_b():
    """All B choices."""
    answers = ["b"] * 24
    result = score_archetype(answers)
    record("arch_all_b_primary", result["primary_archetype"] in ARCHETYPES, f"got {result['primary_archetype']}")
    record("arch_all_b_12_types", len(result["percentages"]) == 12, f"got {len(result['percentages'])} types")


def test_archetype_wrong_count():
    try:
        score_archetype(["a"] * 23)
        record("arch_wrong_count", False, "should have raised ValueError")
    except ValueError:
        record("arch_wrong_count", True)


def test_consciousness_mid():
    """Mid-range answers (3) should be around 310 (Willingness)."""
    answers = [3] * 10
    result = score_consciousness(answers)
    record("con_mid_level", 200 <= result["level"] <= 400, f"level={result['level']}")
    record("con_mid_name", result["level_name"] in [n for _, n in HAWKINS_LEVELS], f"name={result['level_name']}")


def test_consciousness_max():
    """All 5s should give high consciousness."""
    answers = [5] * 10
    result = score_consciousness(answers)
    record("con_max_level", result["level"] >= 500, f"level={result['level']}")


def test_consciousness_min():
    """All 1s should give low consciousness."""
    answers = [1] * 10
    result = score_consciousness(answers)
    record("con_min_level", result["level"] <= 50, f"level={result['level']}")


def test_consciousness_wrong_count():
    try:
        score_consciousness([3] * 9)
        record("con_wrong_count", False, "should have raised ValueError")
    except ValueError:
        record("con_wrong_count", True)


# ============================================================
# SECTION 3 — INTEGRATION TESTS (question banks)
# ============================================================

def test_question_banks():
    from app.services.questions import (
        ARCHETYPE_QUESTIONS,
        BIG_FIVE_QUESTIONS,
        CONSCIOUSNESS_QUESTIONS,
        DAILY_PROMPTS,
    )
    record("qbank_bf_count", len(BIG_FIVE_QUESTIONS) == 50, f"got {len(BIG_FIVE_QUESTIONS)}")
    record("qbank_arch_count", len(ARCHETYPE_QUESTIONS) == 24, f"got {len(ARCHETYPE_QUESTIONS)}")
    record("qbank_con_count", len(CONSCIOUSNESS_QUESTIONS) == 10, f"got {len(CONSCIOUSNESS_QUESTIONS)}")
    record("qbank_prompts", len(DAILY_PROMPTS) >= 5, f"got {len(DAILY_PROMPTS)}")

    # Each BF question has 'text' and 'trait'
    for i, q in enumerate(BIG_FIVE_QUESTIONS):
        if "text" not in q or "trait" not in q:
            record(f"qbank_bf_shape_{i}", False, f"missing text or trait in item {i}")
            return
    record("qbank_bf_shape", True)

    # Each archetype question has a, b, a_type, b_type
    for i, q in enumerate(ARCHETYPE_QUESTIONS):
        if "a" not in q or "b" not in q or "a_type" not in q or "b_type" not in q:
            record(f"qbank_arch_shape_{i}", False, f"missing fields in item {i}")
            return
    record("qbank_arch_shape", True)

    # Each consciousness question has 'text'
    for i, q in enumerate(CONSCIOUSNESS_QUESTIONS):
        if "text" not in q:
            record(f"qbank_con_shape_{i}", False, f"missing text in item {i}")
            return
    record("qbank_con_shape", True)


# ============================================================
# SECTION 4 — API SMOKE TESTS
# ============================================================

async def api_tests():
    """Test live API endpoints."""
    async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as c:
        # Health
        r = await c.get("/api/health")
        record("api_health", r.status_code == 200 and r.json().get("status") == "ok", f"{r.status_code}")

        # Questions - Big Five
        r = await c.get("/api/questions/big-five")
        record("api_q_bf", r.status_code == 200 and r.json().get("total") == 50, f"{r.status_code}")

        # Questions - Archetype
        r = await c.get("/api/questions/archetype")
        record("api_q_arch", r.status_code == 200 and r.json().get("total") == 24, f"{r.status_code}")

        # Questions - Consciousness
        r = await c.get("/api/questions/consciousness")
        record("api_q_con", r.status_code == 200 and r.json().get("total") == 10, f"{r.status_code}")

        # Questions - Daily prompt
        r = await c.get("/api/questions/daily-prompt")
        record("api_q_daily", r.status_code == 200 and "prompt" in r.json(), f"{r.status_code}")

        # Big Five submission validation
        r = await c.post("/api/assessments/big-five", json={"answers": [3] * 49})
        record("api_bf_validation", r.status_code == 400, f"expected 400, got {r.status_code}")

        r = await c.post("/api/assessments/big-five", json={"answers": [6] + [3] * 49})
        record("api_bf_range_validation", r.status_code == 400, f"expected 400, got {r.status_code}")

        # Archetype submission validation
        r = await c.post("/api/assessments/archetype", json={"answers": ["a"] * 23})
        record("api_arch_validation", r.status_code == 400, f"expected 400, got {r.status_code}")

        r = await c.post("/api/assessments/archetype", json={"answers": ["c"] + ["a"] * 23})
        record("api_arch_choice_validation", r.status_code == 400, f"expected 400, got {r.status_code}")

        # Consciousness submission validation
        r = await c.post("/api/assessments/consciousness", json={"answers": [3] * 9})
        record("api_con_validation", r.status_code == 400, f"expected 400, got {r.status_code}")

        # Journal validation - empty
        r = await c.post("/api/journal", json={"prompt": "test", "entry_text": "  "})
        record("api_journal_empty", r.status_code == 400, f"expected 400, got {r.status_code}")

        # Journal validation - too long
        r = await c.post("/api/journal", json={"prompt": "test", "entry_text": "x" * 10001})
        record("api_journal_too_long", r.status_code == 400, f"expected 400, got {r.status_code}")

        # History
        r = await c.get("/api/history")
        record("api_history", r.status_code == 200 and isinstance(r.json(), list), f"{r.status_code}")

        # Profile
        r = await c.get("/api/profile")
        record("api_profile", r.status_code == 200 and "total_assessments" in r.json(), f"{r.status_code}")


# ============================================================
# SECTION 5 — CONFIDENCE STAMP
# ============================================================

def main():
    print(f"\n{'='*60}")
    print(f"  KNOWYOURSELF BEAST TESTS (run_id: {_RUN_ID})")
    print(f"{'='*60}\n")

    print("[UNIT] Scoring algorithms:")
    test_big_five_all_threes()
    test_big_five_extreme_high()
    test_big_five_max_extraversion()
    test_big_five_min_extraversion()
    test_big_five_wrong_count()
    test_archetype_all_a()
    test_archetype_all_b()
    test_archetype_wrong_count()
    test_consciousness_mid()
    test_consciousness_max()
    test_consciousness_min()
    test_consciousness_wrong_count()

    print("\n[INTEGRATION] Question banks:")
    test_question_banks()

    print("\n[API] Smoke tests:")
    asyncio.run(api_tests())

    print(f"\n{'='*60}")
    total = len(passed) + len(failed)
    print(f"  RESULTS: {len(passed)}/{total} passed")
    if failed:
        print(f"  FAILED: {', '.join(failed)}")
    print(f"{'='*60}\n")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
