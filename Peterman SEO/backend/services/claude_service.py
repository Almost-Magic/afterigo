"""
Peterman V4.1 — Claude CLI Service
Almost Magic Tech Lab

Primary AI Engine: Claude CLI (free with Anthropic Max subscription)
Fallback: Ollama (local)

Claude CLI: claude --print --no-input -p "prompt"
"""
import subprocess
import logging
import json

logger = logging.getLogger(__name__)


class ClaudeService:
    """Interface to Claude CLI for local LLM inference."""
    
    def __init__(self):
        self.available = None  # Cache availability check
    
    def is_available(self) -> bool:
        """Check if Claude CLI is installed and available."""
        if self.available is not None:
            return self.available
        
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=10
            )
            self.available = result.returncode == 0
            return self.available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.available = False
            return False
    
    def generate(self, prompt: str, system: str = None, max_tokens: int = 4096, timeout: int = 120) -> dict:
        """
        Generate a completion using Claude CLI.
        
        Returns:
            dict with keys: text, model, tokens_used, cost, engine
        """
        if not self.is_available():
            return {"text": "", "model": "claude-cli", "error": "not_available", "cost": 0.0}
        
        try:
            # Build the prompt
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            
            # Run Claude CLI
            result = subprocess.run(
                ["claude", "--print", "--no-input", "-p", full_prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return {"text": "", "model": "claude-cli", "error": result.stderr, "cost": 0.0}
            
            # Estimate tokens (rough: 4 chars per token)
            text = result.stdout.strip()
            estimated_tokens = len(text) // 4
            
            return {
                "text": text,
                "model": "claude-cli",
                "tokens_used": estimated_tokens,
                "cost": 0.0,  # Claude CLI is free with subscription
                "engine": "claude-cli"
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timeout")
            return {"text": "", "model": "claude-cli", "error": "timeout", "cost": 0.0}
        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return {"text": "", "model": "claude-cli", "error": str(e), "cost": 0.0}
    
    def generate_json(self, prompt: str, system: str = None, timeout: int = 120) -> dict:
        """
        Generate structured JSON output using Claude CLI.
        
        Returns:
            dict with keys: text, parsed (dict), model, error
        """
        json_prompt = f"""{prompt}

Respond with valid JSON only. No markdown, no explanation, just JSON."""
        
        result = self.generate(json_prompt, system=system, timeout=timeout)
        
        if result.get("error"):
            return result
        
        # Try to parse JSON
        text = result["text"].strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        
        try:
            parsed = json.loads(text)
            result["parsed"] = parsed
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            result["parsed"] = None
            result["parse_error"] = str(e)
        
        return result
    
    def health_check(self) -> dict:
        """Check Claude CLI availability."""
        return {
            "status": "ok" if self.is_available() else "unavailable",
            "engine": "claude-cli",
            "version": self._get_version() if self.is_available() else None
        }
    
    def _get_version(self) -> str:
        """Get Claude CLI version."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"


# Singleton
claude = ClaudeService()
