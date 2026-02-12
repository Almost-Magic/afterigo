"""KnowYourself — Ollama integration for AI interpretations.

Routes through Supervisor (:9000) first, falls back to direct Ollama (:11434).
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TIMEOUT = 300.0  # 5 min for cold model loads


async def generate_interpretation(prompt: str) -> str | None:
    """Send a prompt to Ollama and return the response text."""
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 500},
    }

    # Try Supervisor first
    for base_url in [settings.supervisor_url, settings.ollama_url]:
        url = f"{base_url}/api/generate"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", "").strip()
                logger.warning("Ollama %s returned %s", base_url, resp.status_code)
        except Exception as e:
            logger.warning("Ollama %s failed: %s", base_url, e)

    logger.error("All Ollama endpoints failed")
    return None


async def interpret_big_five(scores: dict) -> str | None:
    prompt = (
        "You are a personality psychology expert. A person has completed the Big Five "
        "personality assessment (IPIP-NEO-PI). Their scores (0-100 scale) are:\n"
        f"  Openness: {scores['openness']}\n"
        f"  Conscientiousness: {scores['conscientiousness']}\n"
        f"  Extraversion: {scores['extraversion']}\n"
        f"  Agreeableness: {scores['agreeableness']}\n"
        f"  Neuroticism: {scores['neuroticism']}\n\n"
        "Write a warm, insightful 2-paragraph interpretation of what these scores "
        "suggest about this person's personality. Be encouraging but honest. "
        "Use Australian English spelling."
    )
    return await generate_interpretation(prompt)


async def interpret_archetype(primary: str, shadow: str, percentages: dict) -> str | None:
    top_3 = sorted(percentages.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = ", ".join(f"{k} ({v}%)" for k, v in top_3)
    prompt = (
        f"You are a Jungian psychology expert. A person's primary archetype is the "
        f"{primary} and their shadow archetype is the {shadow}. "
        f"Their top three archetypes are: {top_str}.\n\n"
        f"Write a warm, insightful 2-paragraph interpretation of what the {primary} "
        f"archetype means for this person's life, motivations, and blind spots. "
        f"Briefly mention how the {shadow} shadow may manifest. "
        f"Use Australian English spelling."
    )
    return await generate_interpretation(prompt)


async def interpret_consciousness(level: int, level_name: str) -> str | None:
    prompt = (
        f"You are a consciousness researcher familiar with David Hawkins' Map of Consciousness. "
        f"A person's current estimated level is {level} ({level_name}).\n\n"
        f"Write a brief, compassionate 1-paragraph reflection on what this level means "
        f"for their current state of being. If they are below Courage (200), gently suggest "
        f"what might help them move upward. If above, acknowledge their growth. "
        f"Use Australian English spelling."
    )
    return await generate_interpretation(prompt)


async def reflect_on_journal(prompt_text: str, entry_text: str) -> tuple[str | None, list[str]]:
    """Reflect on a journal entry and extract themes."""
    prompt = (
        f"You are a contemplative guide inspired by Krishnamurti and Ramana Maharshi. "
        f"A person was asked: '{prompt_text}' and wrote:\n\n"
        f'"{entry_text}"\n\n'
        f"Respond in two parts:\n"
        f"1. REFLECTION: A gentle, non-judgmental 1-paragraph reflection that mirrors "
        f"back what you notice without prescribing solutions.\n"
        f"2. THEMES: A comma-separated list of 3-5 single-word themes you notice "
        f"(e.g., identity, restlessness, gratitude, fear, connection).\n\n"
        f"Format:\nREFLECTION: ...\nTHEMES: theme1, theme2, theme3"
    )
    text = await generate_interpretation(prompt)
    if not text:
        return None, []

    reflection = text
    themes = []
    if "THEMES:" in text:
        parts = text.split("THEMES:", 1)
        reflection = parts[0].replace("REFLECTION:", "").strip()
        themes = [t.strip().lower() for t in parts[1].strip().split(",") if t.strip()]

    return reflection, themes
