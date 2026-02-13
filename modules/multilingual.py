"""
ELAINE v3 — Phase 4: Multilingual Intelligence Module
Detects and responds in Tamil, Telugu, Hindi, Japanese, Korean, and 20+ languages.
Uses langdetect for identification and Ollama for multilingual generation.
"""

import re
import json
import logging
from datetime import datetime

logger = logging.getLogger("elaine.multilingual")

# ─────────────────────────────────────────────────────────────
# Language Detection — Script-based (faster & more reliable than langdetect for short text)
# ─────────────────────────────────────────────────────────────

SCRIPT_RANGES = {
    "tamil": [
        (0x0B80, 0x0BFF),  # Tamil block
    ],
    "telugu": [
        (0x0C00, 0x0C7F),  # Telugu block
    ],
    "hindi": [
        (0x0900, 0x097F),  # Devanagari block
    ],
    "kannada": [
        (0x0C80, 0x0CFF),  # Kannada block
    ],
    "malayalam": [
        (0x0D00, 0x0D7F),  # Malayalam block
    ],
    "bengali": [
        (0x0980, 0x09FF),  # Bengali block
    ],
    "gujarati": [
        (0x0A80, 0x0AFF),  # Gujarati block
    ],
    "punjabi": [
        (0x0A00, 0x0A7F),  # Gurmukhi block
    ],
    "japanese": [
        (0x3040, 0x309F),  # Hiragana
        (0x30A0, 0x30FF),  # Katakana
        (0x4E00, 0x9FFF),  # CJK Unified (shared with Chinese)
    ],
    "korean": [
        (0xAC00, 0xD7AF),  # Hangul Syllables
        (0x1100, 0x11FF),  # Hangul Jamo
    ],
    "chinese": [
        (0x4E00, 0x9FFF),  # CJK Unified
        (0x3400, 0x4DBF),  # CJK Extension A
    ],
    "arabic": [
        (0x0600, 0x06FF),  # Arabic block
    ],
    "thai": [
        (0x0E00, 0x0E7F),  # Thai block
    ],
}

# Greetings in supported languages
GREETINGS = {
    "english": "Hello Mani! How can I help?",
    "tamil": "வணக்கம் மணி! எப்படி உதவ முடியும்?",
    "telugu": "నమస్కారం మణి! నేను ఎలా సహాయం చేయగలను?",
    "hindi": "नमस्ते मणि! मैं कैसे मदद कर सकती हूँ?",
    "kannada": "ನಮಸ್ಕಾರ ಮಣಿ! ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    "malayalam": "നമസ്കാരം മണി! ഞാൻ എങ്ങനെ സഹായിക്കാം?",
    "bengali": "নমস্কার মণি! আমি কিভাবে সাহায্য করতে পারি?",
    "japanese": "こんにちは、マニさん！何かお手伝いできますか？",
    "korean": "안녕하세요 마니님! 무엇을 도와드릴까요?",
    "chinese": "你好 Mani！我能帮什么忙？",
    "arabic": "مرحباً ماني! كيف يمكنني مساعدتك؟",
    "thai": "สวัสดีค่ะ Mani! ให้ช่วยอะไรคะ?",
}

# Language names for UI display
LANGUAGE_NAMES = {
    "english": "English",
    "tamil": "தமிழ்",
    "telugu": "తెలుగు",
    "hindi": "हिन्दी",
    "kannada": "ಕನ್ನಡ",
    "malayalam": "മലയാളം",
    "bengali": "বাংলা",
    "gujarati": "ગુજરાતી",
    "punjabi": "ਪੰਜਾਬੀ",
    "japanese": "日本語",
    "korean": "한국어",
    "chinese": "中文",
    "arabic": "العربية",
    "thai": "ไทย",
}


def detect_script(text: str) -> str:
    """
    Detect language from Unicode script ranges.
    More reliable than statistical detection for short texts (e.g. "வணக்கம்").
    Falls back to 'english' for Latin script.
    """
    script_counts = {}

    for char in text:
        code = ord(char)
        for lang, ranges in SCRIPT_RANGES.items():
            for start, end in ranges:
                if start <= code <= end:
                    script_counts[lang] = script_counts.get(lang, 0) + 1
                    break

    if not script_counts:
        return "english"

    # Handle Japanese vs Chinese ambiguity (CJK block is shared)
    if "japanese" in script_counts and "chinese" in script_counts:
        # If hiragana/katakana present, it's Japanese
        jp_unique = sum(1 for c in text if 0x3040 <= ord(c) <= 0x30FF)
        if jp_unique > 0:
            return "japanese"
        return "chinese"

    return max(script_counts, key=script_counts.get)


def detect_language(text: str) -> str:
    """
    Primary language detection. Uses script detection first,
    then falls back to langdetect for Latin-script languages.
    """
    # Strip whitespace and check for empty
    clean = text.strip()
    if not clean:
        return "english"

    # Try script-based detection first (handles Tamil, Telugu, Hindi, etc.)
    script_lang = detect_script(clean)
    if script_lang != "english":
        return script_lang

    # For Latin-script text, try langdetect if available
    try:
        from langdetect import detect
        detected = detect(clean)
        # Map ISO 639-1 codes to our language names
        iso_map = {
            "en": "english", "ta": "tamil", "te": "telugu",
            "hi": "hindi", "kn": "kannada", "ml": "malayalam",
            "bn": "bengali", "gu": "gujarati", "pa": "punjabi",
            "ja": "japanese", "ko": "korean", "zh-cn": "chinese",
            "zh-tw": "chinese", "ar": "arabic", "th": "thai",
            "fr": "french", "de": "german", "es": "spanish",
            "pt": "portuguese", "it": "italian", "nl": "dutch",
            "ru": "russian",
        }
        return iso_map.get(detected, "english")
    except Exception:
        return "english"


def get_ollama_language_instruction(lang: str) -> str:
    """
    Returns a system prompt instruction telling Ollama to respond in the detected language.
    """
    if lang == "english":
        return ""

    lang_name = LANGUAGE_NAMES.get(lang, lang.title())
    return (
        f"\n\nIMPORTANT: The user is communicating in {lang_name}. "
        f"You MUST respond entirely in {lang_name}. "
        f"Use the {lang_name} script naturally. "
        f"If you need to include English technical terms, transliterate them into {lang_name} script "
        f"or keep them in parentheses."
    )


def get_greeting(lang: str) -> str:
    """Get a greeting in the detected language."""
    return GREETINGS.get(lang, GREETINGS["english"])


def format_language_badge(lang: str) -> dict:
    """Return language info for the UI badge."""
    return {
        "code": lang,
        "name": LANGUAGE_NAMES.get(lang, "English"),
        "is_rtl": lang in ("arabic",),
    }


class MultilingualProcessor:
    """
    Wraps language detection and response routing for the Elaine pipeline.
    Integrates with the existing NLU and Ollama modules.
    """

    def __init__(self):
        self.conversation_language = "english"
        self.language_history = []
        self.language_switch_count = 0

    def process_input(self, text: str) -> dict:
        """
        Detect language and return processing metadata.
        """
        detected = detect_language(text)

        # Track language switches
        if detected != self.conversation_language:
            self.language_switch_count += 1
            self.language_history.append({
                "from": self.conversation_language,
                "to": detected,
                "timestamp": datetime.now().isoformat(),
            })
            self.conversation_language = detected

        return {
            "language": detected,
            "language_name": LANGUAGE_NAMES.get(detected, "English"),
            "ollama_instruction": get_ollama_language_instruction(detected),
            "is_rtl": detected in ("arabic",),
            "greeting": get_greeting(detected),
            "badge": format_language_badge(detected),
        }

    def get_status(self) -> dict:
        return {
            "current_language": self.conversation_language,
            "language_name": LANGUAGE_NAMES.get(self.conversation_language, "English"),
            "switches": self.language_switch_count,
            "history": self.language_history[-10:],  # Last 10 switches
        }
