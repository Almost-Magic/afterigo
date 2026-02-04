"""
Unit tests for Signal Desktop
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestProjectStructure:
    """Test project structure."""
    
    def test_main_py_exists(self):
        """main.py should exist."""
        assert Path("main.py").exists()
    
    def test_requirements_exists(self):
        """requirements.txt should exist."""
        assert Path("requirements.txt").exists()
    
    def test_readme_exists(self):
        """README.md should exist."""
        assert Path("README.md").exists()


class TestMainModule:
    """Test main.py module."""
    
    def test_main_py_exists(self):
        """main.py should exist."""
        assert Path("main.py").exists()
    
    def test_main_py_syntax(self):
        """main.py should have valid Python syntax."""
        content = Path("main.py").read_text(encoding="utf-8")
        compile(content, "main.py", "exec")
    
    def test_main_py_has_signal_api(self):
        """main.py should define SignalAPI class."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "class SignalAPI" in content
    
    def test_main_py_has_main_function(self):
        """main.py should have main() function."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "def main():" in content
    
    def test_main_py_has_get_html(self):
        """main.py should have get_html() function."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "def get_html():" in content


class TestRequirements:
    """Test requirements.txt."""
    
    def test_has_pywebview(self):
        """requirements.txt should include pywebview."""
        content = Path("requirements.txt").read_text(encoding="utf-8")
        assert "pywebview" in content.lower()


class TestDocumentation:
    """Test documentation files."""
    
    def test_readme_has_title(self):
        """README should have a title."""
        content = Path("README.md").read_text(encoding="utf-8")
        assert "# Signal Desktop" in content
    
    def test_readme_has_installation(self):
        """README should have installation instructions."""
        content = Path("README.md").read_text(encoding="utf-8")
        assert "install" in content.lower() or "setup" in content.lower()
    
    def test_user_manual_exists(self):
        """USER_MANUAL.md should exist."""
        assert Path("USER_MANUAL.md").exists()
    
    def test_user_manual_has_content(self):
        """USER_MANUAL.md should have substantial content."""
        content = Path("USER_MANUAL.md").read_text(encoding="utf-8")
        assert len(content) > 1000  # Should be substantial


class TestCodeQuality:
    """Test code quality."""
    
    def test_no_hardcoded_secrets(self):
        """No hardcoded API keys."""
        content = Path("main.py").read_text(encoding="utf-8")
        # Check for actual hardcoded keys, not just the words
        assert "sk-" not in content  # OpenAI style key
        assert "AKIA" not in content  # AWS style key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
