"""
Health check engine - validates environment configuration consistency,
detects dependency version drift, and identifies security issues.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthIssue:
    """A single health check issue."""
    severity: Severity
    category: str
    message: str
    detail: str = ""
    suggestion: str = ""


@dataclass
class HealthReport:
    """Complete health check report."""
    score: int = 100
    total_checks: int = 0
    passed_checks: int = 0
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.score >= 90:
            return "healthy"
        elif self.score >= 70:
            return "degraded"
        elif self.score >= 50:
            return "unhealthy"
        return "critical"


class HealthChecker:
    """Environment health check engine."""

    def __init__(self, snapshot: dict, project_path: str = "."):
        self.snapshot = snapshot
        self.project_path = Path(project_path).resolve()
        self.report = HealthReport()

    def run_all_checks(self) -> HealthReport:
        """Run all health checks."""
        self._check_env_files()
        self._check_gitignore()
        self._check_dependency_lock()
        self._check_dependency_consistency()
        self._check_outdated_dependencies()
        self._check_security_issues()
        self._check_config_files()
        self._check_docker_config()
        self._check_readme()
        self._check_license()
        self._check_python_specific()
        self._check_node_specific()
        self._check_go_specific()
        self._check_rust_specific()

        # Calculate score
        for issue in self.report.issues:
            if issue.severity == Severity.CRITICAL:
                self.report.score -= 20
            elif issue.severity == Severity.ERROR:
                self.report.score -= 10
            elif issue.severity == Severity.WARNING:
                self.report.score -= 5
            elif issue.severity == Severity.INFO:
                self.report.score -= 1

        self.report.score = max(0, min(100, self.report.score))
        return self.report

    def _add_issue(self, severity: Severity, category: str, message: str,
                   detail: str = "", suggestion: str = ""):
        """Add a health check issue."""
        self.report.issues.append(HealthIssue(
            severity=severity, category=category, message=message,
            detail=detail, suggestion=suggestion
        ))
        self.report.total_checks += 1
        if severity == Severity.INFO:
            self.report.passed_checks += 1

    def _check_env_files(self):
        """Check environment file configuration."""
        self.report.total_checks += 1
        env_file = self.project_path / ".env"
        env_example = self.project_path / ".env.example"

        if env_file.exists() and not env_example.exists():
            self._add_issue(
                Severity.WARNING, "Environment",
                ".env file exists but .env.example is missing",
                "Create .env.example to document required environment variables",
                "Run: envforge generate --env-example"
            )
        elif env_example.exists():
            # Check if .env.example has actual placeholders
            try:
                content = env_example.read_text()
                if "your-" in content or "TODO" in content or "changeme" in content.lower():
                    self._add_issue(
                        Severity.INFO, "Environment",
                        ".env.example contains placeholder values",
                        "Consider adding more descriptive default values"
                    )
            except (FileNotFoundError, PermissionError):
                pass
        else:
            self._add_issue(
                Severity.INFO, "Environment",
                "No .env or .env.example files detected",
                "Consider creating .env.example for environment documentation"
            )

        # Check if .env is in .gitignore
        self.report.total_checks += 1
        gitignore = self.project_path / ".gitignore"
        if gitignore.exists() and env_file.exists():
            try:
                content = gitignore.read_text()
                if ".env" not in content:
                    self._add_issue(
                        Severity.CRITICAL, "Security",
                        ".env file is not in .gitignore",
                        "This may cause sensitive data to be committed to version control",
                        "Add '.env' to .gitignore immediately"
                    )
                else:
                    self.report.passed_checks += 1
            except (FileNotFoundError, PermissionError):
                pass

    def _check_gitignore(self):
        """Check .gitignore completeness."""
        self.report.total_checks += 1
        gitignore = self.project_path / ".gitignore"

        if not gitignore.exists():
            self._add_issue(
                Severity.WARNING, "Configuration",
                ".gitignore file is missing",
                "A .gitignore file prevents committing build artifacts and sensitive files",
                "Run: envforge generate --gitignore"
            )
            return

        try:
            content = gitignore.read_text()
            languages = [l["name"] for l in self.snapshot.get("languages", [])]
            missing_patterns = []

            essential_patterns = [".env", "__pycache__/", "node_modules/", "dist/", "build/", ".venv/"]
            for pattern in essential_patterns:
                if pattern not in content:
                    missing_patterns.append(pattern)

            if missing_patterns:
                self._add_issue(
                    Severity.INFO, "Configuration",
                    f".gitignore may be missing common patterns: {', '.join(missing_patterns)}",
                    "Consider adding these patterns to prevent committing unnecessary files"
                )
            else:
                self.report.passed_checks += 1
        except (FileNotFoundError, PermissionError):
            pass

    def _check_dependency_lock(self):
        """Check if dependency lock files are present and committed."""
        self.report.total_checks += 1
        pm_managers = self.snapshot.get("package_managers", [])

        for pm in pm_managers:
            if pm.get("config_file") and not pm.get("lock_file"):
                lock_suggestions = {
                    "pip": "Consider generating a requirements lock file or use pipenv/poetry",
                    "npm": "Run: npm install to generate package-lock.json",
                    "go modules": "Run: go mod tidy to generate go.sum",
                }
                self._add_issue(
                    Severity.WARNING, "Dependencies",
                    f"No lock file found for {pm['name']}",
                    lock_suggestions.get(pm["name"], "Generate a lock file to ensure reproducible builds")
                )
                return

        self.report.passed_checks += 1

    def _check_dependency_consistency(self):
        """Check for dependency consistency across environments."""
        self.report.total_checks += 1
        snapshot_file = self.project_path / "envforge.snapshot.json"

        if not snapshot_file.exists():
            self._add_issue(
                Severity.INFO, "Consistency",
                "No envforge snapshot found for comparison",
                "Run: envforge snapshot create to establish a baseline"
            )
            return

        try:
            saved = json.loads(snapshot_file.read_text())
            current_tools = self.snapshot.get("tools", {})
            saved_tools = saved.get("tools", {})

            mismatches = []
            for tool, version in current_tools.items():
                if tool in saved_tools and saved_tools[tool] != version:
                    mismatches.append(f"{tool}: {saved_tools[tool]} -> {version}")

            if mismatches:
                self._add_issue(
                    Severity.WARNING, "Consistency",
                    f"Tool version mismatches detected: {len(mismatches)}",
                    "\n".join(mismatches),
                    "Run: envforge snapshot update to update the baseline"
                )
            else:
                self.report.passed_checks += 1
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass

    def _check_outdated_dependencies(self):
        """Check for potentially outdated dependencies."""
        self.report.total_checks += 1
        deps = self.snapshot.get("dependencies", {})

        # Check for very old Python packages
        if "python" in deps:
            outdated_indicators = []
            for dep in deps["python"]:
                if dep in ("django==1.11", "flask==0.12", "requests==2.20"):
                    outdated_indicators.append(dep)

            if outdated_indicators:
                self._add_issue(
                    Severity.WARNING, "Dependencies",
                    f"Potentially outdated Python packages detected",
                    ", ".join(outdated_indicators),
                    "Consider upgrading to the latest stable versions"
                )

        self.report.passed_checks += 1

    def _check_security_issues(self):
        """Check for common security issues."""
        # Check for hardcoded secrets
        self.report.total_checks += 1
        dangerous_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "Hardcoded token detected"),
        ]

        found_secrets = []
        for pattern, message in dangerous_patterns:
            for root, _, files in os.walk(self.project_path):
                rel_root = Path(root).relative_to(self.project_path)
                skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv",
                            "dist", "build", ".tox", "target"}
                if any(part in skip_dirs for part in rel_root.parts):
                    continue

                for file in files:
                    if file.endswith((".py", ".js", ".ts", ".go", ".rs", ".env", ".yaml", ".yml", ".json", ".toml")):
                        try:
                            filepath = Path(root) / file
                            content = filepath.read_text(errors='ignore')
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                found_secrets.append(f"{rel_root}/{file}: {message}")
                        except (FileNotFoundError, PermissionError):
                            pass

        if found_secrets:
            self._add_issue(
                Severity.CRITICAL, "Security",
                f"Potential security issues found: {len(found_secrets)}",
                "\n".join(found_secrets[:5]),
                "Move secrets to environment variables and add sensitive files to .gitignore"
            )
        else:
            self.report.passed_checks += 1

    def _check_config_files(self):
        """Check for essential configuration files."""
        self.report.total_checks += 1
        config_files = self.snapshot.get("config_files", [])

        essential = {".gitignore", "README.md"}
        missing = essential - set(config_files)

        if missing:
            self._add_issue(
                Severity.INFO, "Configuration",
                f"Missing recommended files: {', '.join(missing)}",
                "These files help other developers understand and work with the project"
            )
        else:
            self.report.passed_checks += 1

    def _check_docker_config(self):
        """Check Docker configuration."""
        self.report.total_checks += 1
        has_dockerfile = "Dockerfile" in self.snapshot.get("config_files", [])
        has_compose = "docker-compose.yml" in self.snapshot.get("config_files", [])

        if has_dockerfile:
            dockerfile = self.project_path / "Dockerfile"
            try:
                content = dockerfile.read_text()
                if ":latest" in content:
                    self._add_issue(
                        Severity.WARNING, "Docker",
                        "Dockerfile uses :latest tag",
                        "Using :latest can lead to non-reproducible builds",
                        "Pin specific version tags for reproducibility"
                    )
                else:
                    self.report.passed_checks += 1
            except (FileNotFoundError, PermissionError):
                pass
        else:
            self._add_issue(
                Severity.INFO, "Docker",
                "No Dockerfile found",
                "Consider adding a Dockerfile for containerized development/deployment",
                "Run: envforge generate --dockerfile"
            )

    def _check_readme(self):
        """Check README quality."""
        self.report.total_checks += 1
        readme = self.project_path / "README.md"

        if not readme.exists():
            self._add_issue(
                Severity.WARNING, "Documentation",
                "README.md is missing",
                "A good README helps others understand and use your project",
                "Run: envforge generate --readme"
            )
            return

        try:
            content = readme.read_text()
            missing_sections = []
            essential_sections = ["Installation", "Usage", "Quick Start", "Install"]
            for section in essential_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)

            if missing_sections:
                self._add_issue(
                    Severity.INFO, "Documentation",
                    f"README may be missing sections: {', '.join(missing_sections)}",
                    "Consider adding these sections for better documentation"
                )
            else:
                self.report.passed_checks += 1
        except (FileNotFoundError, PermissionError):
            pass

    def _check_license(self):
        """Check for license file."""
        self.report.total_checks += 1
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"]
        has_license = any((self.project_path / lf).exists() for lf in license_files)

        if not has_license:
            self._add_issue(
                Severity.INFO, "Legal",
                "No license file detected",
                "Adding a license clarifies how others can use your project",
                "Consider adding a LICENSE file (MIT, Apache-2.0, etc.)"
            )
        else:
            self.report.passed_checks += 1

    def _check_python_specific(self):
        """Python-specific health checks."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        if "Python" not in languages:
            return

        self.report.total_checks += 1
        pyproject = self.project_path / "pyproject.toml"
        setup_py = self.project_path / "setup.py"

        if not pyproject.exists() and not setup_py.exists():
            self._add_issue(
                Severity.INFO, "Python",
                "No pyproject.toml or setup.py found",
                "Modern Python projects should use pyproject.toml for project metadata",
                "Run: envforge generate --pyproject"
            )
        else:
            self.report.passed_checks += 1

    def _check_node_specific(self):
        """Node.js-specific health checks."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        if "JavaScript" not in languages and "TypeScript" not in languages:
            return

        self.report.total_checks += 1
        pkg = self.project_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text())
                if "scripts" not in data or not data["scripts"]:
                    self._add_issue(
                        Severity.INFO, "Node.js",
                        "package.json has no scripts defined",
                        "Add common scripts: dev, build, test, lint"
                    )
                else:
                    self.report.passed_checks += 1
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        else:
            self.report.passed_checks += 1

    def _check_go_specific(self):
        """Go-specific health checks."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        if "Go" not in languages:
            return

        self.report.total_checks += 1
        go_mod = self.project_path / "go.mod"
        if go_mod.exists():
            self.report.passed_checks += 1
        else:
            self._add_issue(
                Severity.ERROR, "Go",
                "go.mod not found in Go project",
                "Run: go mod init <module-name>"
            )

    def _check_rust_specific(self):
        """Rust-specific health checks."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        if "Rust" not in languages:
            return

        self.report.total_checks += 1
        cargo = self.project_path / "Cargo.toml"
        if cargo.exists():
            self.report.passed_checks += 1
        else:
            self._add_issue(
                Severity.ERROR, "Rust",
                "Cargo.toml not found in Rust project",
                "Run: cargo init"
            )
