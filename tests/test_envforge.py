"""Tests for EnvForge - Environment Detection Engine."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from envforge.detector import EnvironmentDetector, LanguageInfo, FrameworkInfo
from envforge.generator import ConfigGenerator
from envforge.health import HealthChecker, Severity, HealthReport
from envforge.diff import DiffEngine
from envforge.snapshot import SnapshotManager


class TestLanguageDetection:
    """Test language detection functionality."""

    def test_detect_python_project(self):
        """Test detection of a Python project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python project files
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "app.py").write_text("def foo(): pass")
            Path(tmpdir, "requirements.txt").write_text("flask==2.0.0\nrequests>=2.25.0")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            lang_names = [l.name for l in snapshot.languages]
            assert "Python" in lang_names, f"Expected Python in {lang_names}"

    def test_detect_javascript_project(self):
        """Test detection of a JavaScript project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "index.js").write_text("console.log('hello')")
            Path(tmpdir, "app.js").write_text("module.exports = {}")
            Path(tmpdir, "package.json").write_text('{"name": "test", "dependencies": {}}')

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            lang_names = [l.name for l in snapshot.languages]
            assert "JavaScript" in lang_names, f"Expected JavaScript in {lang_names}"

    def test_detect_go_project(self):
        """Test detection of a Go project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.go").write_text('package main\nfunc main() {}')
            Path(tmpdir, "go.mod").write_text("module test\n\ngo 1.22")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            lang_names = [l.name for l in snapshot.languages]
            assert "Go" in lang_names, f"Expected Go in {lang_names}"

    def test_detect_empty_directory(self):
        """Test detection on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            assert len(snapshot.languages) == 0, "Expected no languages in empty dir"
            assert snapshot.project_path == str(Path(tmpdir).resolve())

    def test_detect_multiple_languages(self):
        """Test detection of multi-language project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "index.js").write_text("console.log('hello')")
            Path(tmpdir, "go.mod").write_text("module test")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            lang_names = [l.name for l in snapshot.languages]
            assert "Python" in lang_names
            assert "JavaScript" in lang_names


class TestFrameworkDetection:
    """Test framework detection functionality."""

    def test_detect_django(self):
        """Test Django detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "manage.py").write_text("# Django manage.py")
            Path(tmpdir, "requirements.txt").write_text("django>=4.0")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            fw_names = [f.name for f in snapshot.frameworks]
            assert "Django" in fw_names, f"Expected Django in {fw_names}"

    def test_detect_fastapi(self):
        """Test FastAPI detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("from fastapi import FastAPI")
            Path(tmpdir, "requirements.txt").write_text("fastapi>=0.100")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            fw_names = [f.name for f in snapshot.frameworks]
            assert "FastAPI" in fw_names, f"Expected FastAPI in {fw_names}"


class TestPackageManagerDetection:
    """Test package manager detection."""

    def test_detect_npm(self):
        """Test npm detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            pm_names = [pm.name for pm in snapshot.package_managers]
            assert "npm" in pm_names, f"Expected npm in {pm_names}"

    def test_detect_poetry(self):
        """Test Poetry detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "pyproject.toml").write_text("[tool.poetry]\nname = 'test'")
            Path(tmpdir, "poetry.lock").write_text("")

            detector = EnvironmentDetector(tmpdir)
            snapshot = detector.detect_all()

            pm_names = [pm.name for pm in snapshot.package_managers]
            assert "poetry" in pm_names, f"Expected poetry in {pm_names}"


class TestConfigGenerator:
    """Test configuration file generation."""

    def _get_python_snapshot(self):
        """Create a minimal Python snapshot for testing."""
        return {
            "project_path": "/tmp/test",
            "os_info": {"system": "Linux", "release": "5.15"},
            "languages": [{"name": "Python", "version": "3.12.0", "confidence": 1.0, "files_count": 5}],
            "frameworks": [{"name": "FastAPI", "category": "Web Framework", "version": "", "config_files": []}],
            "package_managers": [{"name": "pip", "lock_file": "", "config_file": "requirements.txt", "version": ""}],
            "tools": {"git": "git version 2.40", "python3": "Python 3.12.0"},
            "config_files": ["requirements.txt"],
            "dependencies": {"python": ["fastapi", "uvicorn"]},
        }

    def test_generate_env_example(self):
        """Test .env.example generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = self._get_python_snapshot()
            generator = ConfigGenerator(snapshot, tmpdir)
            content = generator._generate_env_example()

            assert "APP_NAME" in content
            assert "APP_ENV" in content
            assert "DATABASE_URL" in content

    def test_generate_dockerfile_python(self):
        """Test Python Dockerfile generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = self._get_python_snapshot()
            generator = ConfigGenerator(snapshot, tmpdir)
            content = generator._generate_dockerfile()

            assert content is not None
            assert "FROM python:" in content
            assert "WORKDIR" in content

    def test_generate_gitignore(self):
        """Test .gitignore generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = self._get_python_snapshot()
            generator = ConfigGenerator(snapshot, tmpdir)
            content = generator._generate_gitignore()

            assert ".env" in content
            assert "__pycache__/" in content
            assert ".venv/" in content

    def test_generate_makefile(self):
        """Test Makefile generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = self._get_python_snapshot()
            generator = ConfigGenerator(snapshot, tmpdir)
            content = generator._generate_makefile()

            assert "install:" in content
            assert "dev:" in content
            assert "test:" in content

    def test_generate_docker_compose(self):
        """Test docker-compose.yml generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = self._get_python_snapshot()
            generator = ConfigGenerator(snapshot, tmpdir)
            content = generator._generate_docker_compose()

            assert "services:" in content
            assert "app:" in content


class TestHealthChecker:
    """Test health check functionality."""

    def test_check_missing_gitignore(self):
        """Test detection of missing .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = {
                "project_path": tmpdir,
                "languages": [],
                "frameworks": [],
                "package_managers": [],
                "tools": {},
                "config_files": [],
                "dependencies": {},
            }
            checker = HealthChecker(snapshot, tmpdir)
            report = checker.run_all_checks()

            categories = [i.category for i in report.issues]
            assert "Configuration" in categories, "Expected .gitignore warning"

    def test_check_missing_readme(self):
        """Test detection of missing README."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, ".gitignore").write_text(".env")
            snapshot = {
                "project_path": tmpdir,
                "languages": [],
                "frameworks": [],
                "package_managers": [],
                "tools": {},
                "config_files": [".gitignore"],
                "dependencies": {},
            }
            checker = HealthChecker(snapshot, tmpdir)
            report = checker.run_all_checks()

            categories = [i.category for i in report.issues]
            assert "Documentation" in categories, "Expected README warning"

    def test_check_env_not_in_gitignore(self):
        """Test detection of .env not in .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, ".env").write_text("SECRET=abc123")
            Path(tmpdir, ".gitignore").write_text("__pycache__/")
            Path(tmpdir, "README.md").write_text("# Test")

            snapshot = {
                "project_path": tmpdir,
                "languages": [],
                "frameworks": [],
                "package_managers": [],
                "tools": {},
                "config_files": [".gitignore", "README.md", ".env"],
                "dependencies": {},
            }
            checker = HealthChecker(snapshot, tmpdir)
            report = checker.run_all_checks()

            severities = [(i.severity, i.category) for i in report.issues]
            assert any(s == Severity.CRITICAL and c == "Security" for s, c in severities), \
                "Expected critical security issue for .env not in .gitignore"


class TestDiffEngine:
    """Test environment diff functionality."""

    def test_identical_environments(self):
        """Test diff with identical environments."""
        snap = {
            "tools": {"git": "2.40", "python3": "3.12"},
            "languages": [{"name": "Python"}],
            "dependencies": {"python": ["flask"]},
            "config_files": ["README.md"],
        }

        engine = DiffEngine(snap, snap)
        result = engine.compare()

        assert len(result.tool_diffs) == 0
        assert len(result.dep_diffs) == 0

    def test_different_tools(self):
        """Test diff with different tool versions."""
        snap_a = {"tools": {"git": "2.40", "python3": "3.12"}, "languages": [], "dependencies": {}, "config_files": []}
        snap_b = {"tools": {"git": "2.30", "python3": "3.11"}, "languages": [], "dependencies": {}, "config_files": []}

        engine = DiffEngine(snap_a, snap_b)
        result = engine.compare()

        assert len(result.tool_diffs) == 2
        assert all(d["type"] == "version_mismatch" for d in result.tool_diffs)


class TestSnapshotManager:
    """Test snapshot management."""

    def test_save_and_load(self):
        """Test saving and loading snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SnapshotManager(tmpdir)
            snapshot = {
                "project_path": tmpdir,
                "os_info": {"system": "Linux"},
                "languages": [],
                "frameworks": [],
                "package_managers": [],
                "tools": {},
                "config_files": [],
                "dependencies": {},
            }

            path = manager.save(snapshot, name="test")
            assert Path(path).exists()

            loaded = manager.load()
            assert loaded is not None
            assert loaded["os_info"]["system"] == "Linux"

    def test_export_and_import(self):
        """Test exporting and importing snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SnapshotManager(tmpdir)
            snapshot = {"test": "data", "os_info": {"system": "Test"}}

            export_path = os.path.join(tmpdir, "export.json")
            manager.export(snapshot, export_path)

            imported = manager.import_snapshot(export_path)
            assert imported is not None
            assert imported["test"] == "data"


class TestCLI:
    """Test CLI commands."""

    def test_detect_command(self):
        """Test detect command runs without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")

            from envforge.cli import create_parser, cmd_detect
            parser = create_parser()
            args = parser.parse_args(["detect", "--path", tmpdir, "--quiet"])
            cmd_detect(args)  # Should not raise

    def test_info_command(self):
        """Test info command runs without error."""
        from envforge.cli import create_parser, cmd_info
        parser = create_parser()
        args = parser.parse_args(["info"])
        cmd_info(args)  # Should not raise

    def test_generate_dry_run(self):
        """Test generate with dry-run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")

            from envforge.cli import create_parser, cmd_generate
            parser = create_parser()
            args = parser.parse_args(["generate", "--path", tmpdir, "--dry-run"])
            cmd_generate(args)  # Should not raise


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
