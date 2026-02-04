"""
Beast Security Scanner v1.0
Checks for common security issues in code.
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime


class BeastScanner:
    """Security scanner for code analysis."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues = []
        self.warnings = []
    
    def scan(self) -> dict:
        """Run all security checks."""
        print("🔒 BEAST SECURITY SCAN")
        print("=" * 50)
        
        self.check_hardcoded_secrets()
        self.check_dangerous_functions()
        
        return self.generate_report()
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded API keys, passwords, etc."""
        patterns = [
            (r'api[_-]?key\s*=\s*["'][a-zA-Z0-9]{20,}["']', "Hardcoded API key"),
            (r'password\s*=\s*["'][^"']{8,}["']', "Hardcoded password"),
            (r'secret\s*=\s*["'][a-zA-Z0-9]{20,}["']', "Hardcoded secret"),
            (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private key in code"),
        ]
        
        for filepath in self.project_path.rglob("*"):
            if filepath.is_file() and filepath.suffix in [".py", ".js", ".ts", ".json", ".env"]:
                if "__pycache__" in str(filepath) or ".git" in str(filepath):
                    continue
                try:
                    content = filepath.read_text(encoding="utf-8")
                    for pattern, description in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.issues.append({
                                "severity": "CRITICAL",
                                "file": str(filepath.relative_to(self.project_path)),
                                "issue": description
                            })
                except:
                    pass
    
    def check_dangerous_functions(self):
        """Check for dangerous function usage."""
        patterns = [
            (r'\beval\s*\(', "Use of eval()"),
            (r'\bexec\s*\(', "Use of exec()"),
        ]
        
        for filepath in self.project_path.rglob("*.py"):
            if "__pycache__" in str(filepath):
                continue
            try:
                content = filepath.read_text(encoding="utf-8")
                for pattern, description in patterns:
                    if re.search(pattern, content):
                        self.warnings.append({
                            "severity": "WARNING",
                            "file": str(filepath.relative_to(self.project_path)),
                            "issue": description
                        })
            except:
                pass
    
    def generate_report(self) -> dict:
        """Generate security report."""
        report = {
            "scan_time": datetime.now().isoformat(),
            "project": str(self.project_path),
            "summary": {
                "critical": len([i for i in self.issues if i["severity"] == "CRITICAL"]),
                "warnings": len(self.warnings),
                "passed": len(self.issues) == 0
            },
            "issues": self.issues,
            "warnings": self.warnings
        }
        
        print(f"\n📊 SCAN RESULTS")
        print(f"   Critical Issues: {report['summary']['critical']}")
        print(f"   Warnings: {report['summary']['warnings']}")
        print(f"   Status: {'✅ PASSED' if report['summary']['passed'] else '❌ FAILED'}")
        
        return report


def run_beast(project_path: str) -> bool:
    """Run Beast scanner and return True if passed."""
    scanner = BeastScanner(project_path)
    report = scanner.scan()
    
    # Save report
    report_path = Path(project_path) / "reports" / "beast_report.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    return report["summary"]["passed"]


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = run_beast(path)
    sys.exit(0 if success else 1)
