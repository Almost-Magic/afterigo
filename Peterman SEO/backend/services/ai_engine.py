"""
Peterman V4.1 — Unified AI Engine
Almost Magic Tech Lab

Primary: Claude CLI (free with Anthropic Max subscription)
Fallback: Ollama (local via Supervisor :9000)

This module provides a unified interface that tries Claude CLI first,
then falls back to Ollama if Claude is unavailable.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Unified AI Engine with Claude CLI primary, Ollama fallback.
    
    Usage:
        from backend.services.ai_engine import ai_engine
        
        # Generate text
        result = ai_engine.generate("What is AI governance?", system="You are an expert.")
        
        # Generate JSON
        result = ai_engine.generate_json("Return JSON for a brand profile.")
        
        # Get status
        status = ai_engine.get_status()
    """
    
    def __init__(self):
        self._claude = None
        self._ollama = None
    
    @property
    def claude(self):
        """Lazy load Claude service."""
        if self._claude is None:
            from .claude_service import ClaudeService
            self._claude = ClaudeService()
        return self._claude
    
    @property
    def ollama(self):
        """Lazy load Ollama service."""
        if self._ollama is None:
            from .ollama_service import OllamaService
            self._ollama = OllamaService()
        return self._ollama
    
    def generate(
        self,
        prompt: str,
        system: str = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: int = 120
    ) -> dict:
        """
        Generate text using the best available AI engine.
        
        Priority:
        1. Claude CLI (free, high quality)
        2. Ollama (local, gemma2:27b)
        
        Args:
            prompt: The user prompt
            system: System prompt (optional)
            model: Specific model hint (ignored, we choose engine)
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            dict with keys: text, model, tokens_used, cost, engine
        """
        # Try Claude CLI first
        if self.claude.is_available():
            try:
                result = self.claude.generate(
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                if result.get("text") and not result.get("error"):
                    logger.info("AI: Using Claude CLI")
                    return result
            except Exception as e:
                logger.warning(f"Claude CLI failed: {e}")
        
        # Fall back to Ollama
        try:
            result = self.ollama.generate(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if result.get("text") and not result.get("error"):
                logger.info("AI: Using Ollama (fallback)")
                return result
        except Exception as e:
            logger.error(f"Ollama failed: {e}")
        
        # Both failed
        return {
            "text": "",
            "model": "none",
            "tokens_used": 0,
            "cost": 0.0,
            "engine": "none",
            "error": "No AI engine available"
        }
    
    def generate_json(
        self,
        prompt: str,
        system: str = None,
        timeout: int = 120
    ) -> dict:
        """
        Generate structured JSON using the best available AI engine.
        
        Returns:
            dict with keys: text, parsed, model, engine
        """
        # Try Claude CLI first
        if self.claude.is_available():
            try:
                result = self.claude.generate_json(prompt=prompt, system=system, timeout=timeout)
                if result.get("parsed") and not result.get("error"):
                    logger.info("AI JSON: Using Claude CLI")
                    return result
            except Exception as e:
                logger.warning(f"Claude JSON failed: {e}")
        
        # Fall back to Ollama
        try:
            result = self.ollama.generate_json(prompt=prompt, system=system)
            if result.get("parsed") and not result.get("error"):
                logger.info("AI JSON: Using Ollama (fallback)")
                return result
        except Exception as e:
            logger.error(f"Ollama JSON failed: {e}")
        
        return {
            "text": "",
            "parsed": None,
            "model": "none",
            "engine": "none",
            "error": "No AI engine available for JSON generation"
        }
    
    def embed(self, text: str, model: str = None) -> dict:
        """
        Generate embedding vector for text.
        
        Uses Ollama (nomic-embed-text) as Claude CLI doesn't support embeddings.
        
        Returns:
            dict with keys: embedding, model, dimensions, cost
        """
        try:
            result = self.ollama.embed(text=text, model=model)
            if result.get("embedding"):
                return result
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
        
        return {
            "embedding": [],
            "model": "none",
            "dimensions": 0,
            "cost": 0.0,
            "error": "Embedding unavailable"
        }
    
    def get_status(self) -> dict:
        """
        Get the status of all AI engines.
        
        Returns:
            dict with claude_cli, ollama, preferred_engine
        """
        claude_status = self.claude.health_check()
        ollama_status = self.ollama.health_check()
        
        # Determine preferred engine
        preferred = "none"
        if claude_status.get("status") == "ok":
            preferred = "claude-cli"
        elif ollama_status.get("status") == "ok":
            preferred = "ollama"
        
        return {
            "claude_cli": {
                "available": claude_status.get("status") == "ok",
                "version": claude_status.get("version"),
            },
            "ollama": {
                "available": ollama_status.get("status") == "ok",
                "models_available": ollama_status.get("models_available", []),
            },
            "preferred_engine": preferred,
        }
    
    def health_check(self) -> dict:
        """Full health check for all AI services."""
        return {
            "ai_engine": self.get_status(),
            "overall": "healthy" if self.get_status()["preferred_engine"] != "none" else "degraded"
        }


# Singleton instance
ai_engine = AIEngine()


# Convenience wrappers for backward compatibility
def generate(prompt: str, system: str = None, **kwargs) -> dict:
    """Wrapper for ai_engine.generate()."""
    return ai_engine.generate(prompt=prompt, system=system, **kwargs)


def generate_json(prompt: str, system: str = None, **kwargs) -> dict:
    """Wrapper for ai_engine.generate_json()."""
    return ai_engine.generate_json(prompt=prompt, system=system, **kwargs)


def embed(text: str, **kwargs) -> dict:
    """Wrapper for ai_engine.embed()."""
    return ai_engine.embed(text=text, **kwargs)


def get_status() -> dict:
    """Wrapper for ai_engine.get_status()."""
    return ai_engine.get_status()


def health_check() -> dict:
    """Wrapper for ai_engine.health_check()."""
    return ai_engine.health_check()
