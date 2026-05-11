"""
Environment detection engine - automatically scans project directories
to identify tech stacks, languages, frameworks, and package managers.
"""

import os
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class LanguageInfo:
    """Detected language information."""
    name: str
    version: str = ""
    confidence: float = 0.0
    files_count: int = 0


@dataclass
class FrameworkInfo:
    """Detected framework information."""
    name: str
    category: str = ""
    version: str = ""
    config_files: List[str] = field(default_factory=list)


@dataclass
class PackageManagerInfo:
    """Detected package manager information."""
    name: str
    lock_file: str = ""
    config_file: str = ""
    version: str = ""


@dataclass
class EnvironmentSnapshot:
    """Complete environment snapshot."""
    project_path: str = ""
    os_info: Dict[str, str] = field(default_factory=dict)
    languages: List[Dict] = field(default_factory=list)
    frameworks: List[Dict] = field(default_factory=list)
    package_managers: List[Dict] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    tools: Dict[str, str] = field(default_factory=dict)
    config_files: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


# Language detection patterns
LANGUAGE_PATTERNS = {
    "Python": {
        "extensions": [".py", ".pyw", ".pyx", ".pyi"],
        "config_files": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile", "poetry.lock"],
        "version_cmd": ["python3", "--version"],
        "version_pattern": "Python ([\\d.]+)",
    },
    "JavaScript": {
        "extensions": [".js", ".mjs", ".cjs", ".jsx"],
        "config_files": ["package.json", ".babelrc", "babel.config.js", "rollup.config.js", "webpack.config.js"],
        "version_cmd": ["node", "--version"],
        "version_pattern": "v([\\d.]+)",
    },
    "TypeScript": {
        "extensions": [".ts", ".tsx", ".mts", ".cts"],
        "config_files": ["tsconfig.json", "tsconfig.*.json"],
        "version_cmd": ["tsc", "--version"],
        "version_pattern": "Version ([\\d.]+)",
    },
    "Go": {
        "extensions": [".go"],
        "config_files": ["go.mod", "go.sum", "go.work"],
        "version_cmd": ["go", "version"],
        "version_pattern": "go([\\d.]+)",
    },
    "Rust": {
        "extensions": [".rs"],
        "config_files": ["Cargo.toml", "Cargo.lock", "rust-toolchain.toml"],
        "version_cmd": ["rustc", "--version"],
        "version_pattern": "rustc ([\\d.]+)",
    },
    "Java": {
        "extensions": [".java"],
        "config_files": ["pom.xml", "build.gradle", "build.gradle.kts", ".mvn", "mvnw"],
        "version_cmd": ["java", "-version"],
        "version_pattern": 'version "([\\d.]+)"',
    },
    "C/C++": {
        "extensions": [".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hxx"],
        "config_files": ["CMakeLists.txt", "Makefile", "meson.build", "configure.ac"],
        "version_cmd": ["gcc", "--version"],
        "version_pattern": "gcc \\(.*\\) ([\\d.]+)",
    },
    "Ruby": {
        "extensions": [".rb", ".erb", ".rake"],
        "config_files": ["Gemfile", "Rakefile", ".ruby-version", "Gemfile.lock"],
        "version_cmd": ["ruby", "--version"],
        "version_pattern": "ruby ([\\d.]+)",
    },
    "PHP": {
        "extensions": [".php", ".phtml"],
        "config_files": ["composer.json", "composer.lock", "php.ini", ".php-version"],
        "version_cmd": ["php", "--version"],
        "version_pattern": "PHP ([\\d.]+)",
    },
    "Swift": {
        "extensions": [".swift"],
        "config_files": ["Package.swift", ".swift-version", "Podfile"],
        "version_cmd": ["swift", "--version"],
        "version_pattern": "Swift version ([\\d.]+)",
    },
    "Kotlin": {
        "extensions": [".kt", ".kts"],
        "config_files": ["build.gradle.kts", "settings.gradle.kts"],
        "version_cmd": ["kotlin", "-version"],
        "version_pattern": "Kotlin version ([\\d.]+)",
    },
    "Dart": {
        "extensions": [".dart"],
        "config_files": ["pubspec.yaml", "pubspec.lock"],
        "version_cmd": ["dart", "--version"],
        "version_pattern": "Dart SDK version: ([\\d.]+)",
    },
    "Shell": {
        "extensions": [".sh", ".bash", ".zsh", ".fish"],
        "config_files": [".bashrc", ".zshrc", ".profile", ".bash_profile"],
        "version_cmd": ["bash", "--version"],
        "version_pattern": "bash version ([\\d.]+)",
    },
}

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    # Web frameworks
    "Django": {"category": "Web Framework", "files": ["manage.py"], "markers": ["django"]},
    "Flask": {"category": "Web Framework", "files": [], "markers": ["flask"]},
    "FastAPI": {"category": "Web Framework", "files": [], "markers": ["fastapi"]},
    "Express": {"category": "Web Framework", "files": [], "markers": ["express"]},
    "Next.js": {"category": "Web Framework", "files": ["next.config.js", "next.config.mjs", "next.config.ts"], "markers": ["next"]},
    "Nuxt": {"category": "Web Framework", "files": ["nuxt.config.ts", "nuxt.config.js"], "markers": ["nuxt"]},
    "React": {"category": "Frontend Library", "files": [], "markers": ["react"]},
    "Vue": {"category": "Frontend Library", "files": [], "markers": ["vue"]},
    "Svelte": {"category": "Frontend Library", "files": ["svelte.config.js"], "markers": ["svelte"]},
    "Angular": {"category": "Frontend Framework", "files": ["angular.json"], "markers": ["@angular/core"]},
    "Spring Boot": {"category": "Web Framework", "files": [], "markers": ["spring-boot"]},
    "Rails": {"category": "Web Framework", "files": ["config/routes.rb"], "markers": ["rails"]},
    "Laravel": {"category": "Web Framework", "files": ["artisan"], "markers": ["laravel"]},
    "Gin": {"category": "Web Framework", "files": [], "markers": ["gin-gonic/gin"]},
    "Fiber": {"category": "Web Framework", "files": [], "markers": ["gofiber/fiber"]},
    "Actix": {"category": "Web Framework", "files": [], "markers": ["actix-web"]},
    "Axum": {"category": "Web Framework", "files": [], "markers": ["axum"]},
    "Rocket": {"category": "Web Framework", "files": ["Rocket.toml"], "markers": ["rocket"]},
    # AI/ML frameworks
    "PyTorch": {"category": "AI/ML Framework", "files": [], "markers": ["torch", "pytorch"]},
    "TensorFlow": {"category": "AI/ML Framework", "files": [], "markers": ["tensorflow"]},
    "Hugging Face": {"category": "AI/ML Framework", "files": [], "markers": ["transformers", "datasets"]},
    "LangChain": {"category": "AI Framework", "files": [], "markers": ["langchain"]},
    # CLI frameworks
    "Click": {"category": "CLI Framework", "files": [], "markers": ["click"]},
    "Typer": {"category": "CLI Framework", "files": [], "markers": ["typer"]},
    "Clap": {"category": "CLI Framework", "files": [], "markers": ["clap"]},
    "Cobra": {"category": "CLI Framework", "files": [], "markers": ["cobra"]},
    # Testing
    "pytest": {"category": "Testing", "files": ["pytest.ini", "conftest.py"], "markers": ["pytest"]},
    "Jest": {"category": "Testing", "files": ["jest.config.js", "jest.config.ts"], "markers": ["jest"]},
    "Vitest": {"category": "Testing", "files": ["vitest.config.ts"], "markers": ["vitex"]},
    "Go Test": {"category": "Testing", "files": ["*_test.go"], "markers": []},
}

# Package manager detection
PACKAGE_MANAGER_PATTERNS = {
    "pip": {"lock": "requirements.txt", "config": "requirements.txt", "version_cmd": ["pip", "--version"]},
    "pipenv": {"lock": "Pipfile.lock", "config": "Pipfile", "version_cmd": ["pipenv", "--version"]},
    "poetry": {"lock": "poetry.lock", "config": "pyproject.toml", "version_cmd": ["poetry", "--version"]},
    "uv": {"lock": "uv.lock", "config": "pyproject.toml", "version_cmd": ["uv", "--version"]},
    "npm": {"lock": "package-lock.json", "config": "package.json", "version_cmd": ["npm", "--version"]},
    "yarn": {"lock": "yarn.lock", "config": "package.json", "version_cmd": ["yarn", "--version"]},
    "pnpm": {"lock": "pnpm-lock.yaml", "config": "package.json", "version_cmd": ["pnpm", "--version"]},
    "bun": {"lock": "bun.lockb", "config": "package.json", "version_cmd": ["bun", "--version"]},
    "go modules": {"lock": "go.sum", "config": "go.mod", "version_cmd": ["go", "version"]},
    "cargo": {"lock": "Cargo.lock", "config": "Cargo.toml", "version_cmd": ["cargo", "--version"]},
    "maven": {"lock": "", "config": "pom.xml", "version_cmd": ["mvn", "--version"]},
    "gradle": {"lock": "", "config": "build.gradle", "version_cmd": ["gradle", "--version"]},
    "composer": {"lock": "composer.lock", "config": "composer.json", "version_cmd": ["composer", "--version"]},
    "gem": {"lock": "Gemfile.lock", "config": "Gemfile", "version_cmd": ["gem", "--version"]},
    "pub": {"lock": "pubspec.lock", "config": "pubspec.yaml", "version_cmd": ["dart", "pub", "--version"]},
}

# Common development tools to detect
DEV_TOOLS = {
    "git": ["git", "--version"],
    "docker": ["docker", "--version"],
    "docker-compose": ["docker-compose", "--version"],
    "make": ["make", "--version"],
    "cmake": ["cmake", "--version"],
    "gcc": ["gcc", "--version"],
    "node": ["node", "--version"],
    "python3": ["python3", "--version"],
    "pip": ["pip", "--version"],
    "npm": ["npm", "--version"],
    "go": ["go", "version"],
    "rustc": ["rustc", "--version"],
    "cargo": ["cargo", "--version"],
    "java": ["java", "-version"],
    "ruby": ["ruby", "--version"],
    "php": ["php", "--version"],
    "swift": ["swift", "--version"],
    "dotnet": ["dotnet", "--version"],
    "deno": ["deno", "--version"],
    "bun": ["bun", "--version"],
    "pnpm": ["pnpm", "--version"],
    "yarn": ["yarn", "--version"],
    "gradle": ["gradle", "--version"],
    "mvn": ["mvn", "--version"],
    "conda": ["conda", "--version"],
    "poetry": ["poetry", "--version"],
    "uv": ["uv", "--version"],
    "redis-cli": ["redis-cli", "--version"],
    "psql": ["psql", "--version"],
    "mysql": ["mysql", "--version"],
    "mongosh": ["mongosh", "--version"],
}


class EnvironmentDetector:
    """Main environment detection engine."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.snapshot = EnvironmentSnapshot()

    def detect_all(self) -> EnvironmentSnapshot:
        """Run full environment detection."""
        self.snapshot.project_path = str(self.project_path)
        self.snapshot.os_info = self._detect_os_info()
        self.snapshot.languages = self._detect_languages()
        self.snapshot.frameworks = self._detect_frameworks()
        self.snapshot.package_managers = self._detect_package_managers()
        self.snapshot.tools = self._detect_tools()
        self.snapshot.config_files = self._detect_config_files()
        self.snapshot.dependencies = self._detect_dependencies()
        return self.snapshot

    def _detect_os_info(self) -> Dict[str, str]:
        """Detect operating system information."""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }
        if platform.system() == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith(("NAME=", "VERSION=", "ID=")):
                            key, _, value = line.strip().partition("=")
                            info[key.lower()] = value.strip('"')
            except (FileNotFoundError, PermissionError):
                pass
        elif platform.system() == "Darwin":
            try:
                result = subprocess.run(
                    ["sw_vers", "-productVersion"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    info["macos_version"] = result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        return info

    def _detect_languages(self) -> List[LanguageInfo]:
        """Detect programming languages used in the project."""
        detected = []
        extension_counts: Dict[str, int] = {}

        # Count file extensions
        for root, _, files in os.walk(self.project_path):
            # Skip common non-source directories
            rel_root = Path(root).relative_to(self.project_path)
            skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv",
                        "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
                        "target", ".gradle", ".idea", ".vscode"}
            if any(part in skip_dirs for part in rel_root.parts):
                continue

            for file in files:
                ext = Path(file).suffix.lower()
                if ext:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1

        # Match extensions to languages
        for lang_name, patterns in LANGUAGE_PATTERNS.items():
            total_files = sum(
                extension_counts.get(ext, 0)
                for ext in patterns["extensions"]
            )
            if total_files > 0:
                version = self._get_tool_version(
                    patterns["version_cmd"],
                    patterns.get("version_pattern", "")
                )
                confidence = min(total_files / max(total_files, 1), 1.0)
                detected.append(LanguageInfo(
                    name=lang_name,
                    version=version,
                    confidence=confidence,
                    files_count=total_files,
                ))

        # Sort by file count descending
        detected.sort(key=lambda x: x.files_count, reverse=True)
        return detected

    def _detect_frameworks(self) -> List[FrameworkInfo]:
        """Detect frameworks used in the project."""
        detected = []

        # Check config files first
        for fw_name, fw_info in FRAMEWORK_PATTERNS.items():
            config_files = []
            for cf in fw_info["files"]:
                if (self.project_path / cf).exists():
                    config_files.append(cf)

            if config_files:
                version = self._detect_framework_version(fw_name)
                detected.append(FrameworkInfo(
                    name=fw_name,
                    category=fw_info["category"],
                    version=version,
                    config_files=config_files,
                ))
                continue

            # Check dependency markers
            if fw_info["markers"]:
                found_markers = self._check_dependency_markers(fw_info["markers"])
                if found_markers:
                    version = self._detect_framework_version(fw_name)
                    detected.append(FrameworkInfo(
                        name=fw_name,
                        category=fw_info["category"],
                        version=version,
                    ))

        return detected

    def _detect_package_managers(self) -> List[PackageManagerInfo]:
        """Detect package managers used in the project."""
        detected = []

        for pm_name, pm_info in PACKAGE_MANAGER_PATTERNS.items():
            config_path = self.project_path / pm_info["config"]
            lock_path = self.project_path / pm_info["lock"]

            if config_path.exists() or lock_path.exists():
                version = self._get_tool_version(pm_info["version_cmd"], "")
                detected.append(PackageManagerInfo(
                    name=pm_name,
                    lock_file=pm_info["lock"] if lock_path.exists() else "",
                    config_file=pm_info["config"] if config_path.exists() else "",
                    version=version,
                ))

        return detected

    def _detect_tools(self) -> Dict[str, str]:
        """Detect installed development tools."""
        tools = {}
        for tool_name, cmd in DEV_TOOLS.items():
            version = self._get_tool_version(cmd, "")
            if version:
                tools[tool_name] = version
        return tools

    def _detect_config_files(self) -> List[str]:
        """Detect configuration files in the project."""
        config_files = []
        common_configs = [
            ".env", ".env.example", ".env.local", ".env.development", ".env.production",
            ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc", ".prettierrc.js",
            ".eslintrc", ".eslintrc.js", ".eslintrc.json",
            "tsconfig.json", "jsconfig.json",
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore",
            "Makefile", "Taskfile.yml",
            "README.md", "README.rst", "LICENSE", "CONTRIBUTING.md",
            ".github/workflows/", ".vscode/settings.json",
            "pyproject.toml", "setup.py", "setup.cfg", "tox.ini",
            "package.json", ".babelrc",
            "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
            "Gemfile", "composer.json", "pubspec.yaml",
        ]
        for cf in common_configs:
            path = self.project_path / cf
            if path.exists():
                config_files.append(cf)
        return sorted(config_files)

    def _detect_dependencies(self) -> Dict[str, List[str]]:
        """Detect project dependencies from various config files."""
        deps = {}

        # Python requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            deps["python"] = self._parse_requirements(req_file)

        # Python pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            py_deps = self._parse_pyproject(pyproject)
            if py_deps:
                deps["python"] = deps.get("python", []) + py_deps

        # Node.js package.json
        pkg_json = self.project_path / "package.json"
        if pkg_json.exists():
            node_deps = self._parse_package_json(pkg_json)
            if node_deps:
                deps["node"] = node_deps

        # Go go.mod
        go_mod = self.project_path / "go.mod"
        if go_mod.exists():
            go_deps = self._parse_go_mod(go_mod)
            if go_deps:
                deps["go"] = go_deps

        # Rust Cargo.toml
        cargo_toml = self.project_path / "Cargo.toml"
        if cargo_toml.exists():
            rust_deps = self._parse_cargo_toml(cargo_toml)
            if rust_deps:
                deps["rust"] = rust_deps

        return deps

    def _parse_requirements(self, filepath: Path) -> List[str]:
        """Parse requirements.txt file."""
        deps = []
        try:
            with open(filepath) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        # Extract package name (before any version specifier)
                        pkg = line.split(">=")[0].split("==")[0].split("<=")[0].split("~=")[0].split("!=")[0].split("[")[0].strip()
                        if pkg:
                            deps.append(pkg)
        except (FileNotFoundError, PermissionError):
            pass
        return deps

    def _parse_pyproject(self, filepath: Path) -> List[str]:
        """Parse pyproject.toml for dependencies."""
        deps = []
        try:
            content = filepath.read_text()
            # Simple TOML parsing for dependencies section
            in_deps = False
            in_dev_deps = False
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("dependencies =") or stripped.startswith("[project.dependencies]"):
                    in_deps = True
                    in_dev_deps = False
                    continue
                if stripped.startswith("[") and "dependencies" not in stripped:
                    in_deps = False
                if in_deps and stripped and not stripped.startswith("#") and not stripped.startswith("["):
                    pkg = stripped.split("=")[0].strip().strip('"').strip("'")
                    if pkg:
                        deps.append(pkg)
        except (FileNotFoundError, PermissionError):
            pass
        return deps

    def _parse_package_json(self, filepath: Path) -> List[str]:
        """Parse package.json for dependencies."""
        deps = []
        try:
            content = json.loads(filepath.read_text())
            for section in ["dependencies", "devDependencies"]:
                if section in content:
                    deps.extend(content[section].keys())
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            pass
        return deps

    def _parse_go_mod(self, filepath: Path) -> List[str]:
        """Parse go.mod for dependencies."""
        deps = []
        try:
            with open(filepath) as f:
                in_require = False
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("require ("):
                        in_require = True
                        continue
                    if in_require and stripped == ")":
                        break
                    if in_require and stripped and not stripped.startswith("//"):
                        parts = stripped.split()
                        if parts:
                            deps.append(parts[0])
        except (FileNotFoundError, PermissionError):
            pass
        return deps

    def _parse_cargo_toml(self, filepath: Path) -> List[str]:
        """Parse Cargo.toml for dependencies."""
        deps = []
        try:
            content = filepath.read_text()
            in_deps = False
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("[dependencies]"):
                    in_deps = True
                    continue
                if stripped.startswith("[") and stripped != "[dependencies]":
                    in_deps = False
                if in_deps and stripped and not stripped.startswith("#"):
                    pkg = stripped.split("=")[0].strip()
                    if pkg:
                        deps.append(pkg)
        except (FileNotFoundError, PermissionError):
            pass
        return deps

    def _get_tool_version(self, cmd: List[str], pattern: str) -> str:
        """Get version string from a tool command."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.strip() or result.stderr.strip()
                if pattern:
                    import re
                    match = re.search(pattern, output)
                    if match:
                        return match.group(1)
                return output.split("\n")[0]
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass
        return ""

    def _detect_framework_version(self, framework_name: str) -> str:
        """Try to detect framework version."""
        version_commands = {
            "Django": ["python3", "-c", "import django; print(django.__version__)"],
            "Flask": ["python3", "-c", "import flask; print(flask.__version__)"],
            "FastAPI": ["python3", "-c", "import fastapi; print(fastapi.__version__)"],
        }
        cmd = version_commands.get(framework_name)
        if cmd:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        return ""

    def _check_dependency_markers(self, markers: List[str]) -> List[str]:
        """Check if dependency markers exist in project files."""
        found = []
        # Check Python files
        for marker in markers:
            # Check requirements.txt
            req_file = self.project_path / "requirements.txt"
            if req_file.exists():
                try:
                    content = req_file.read_text()
                    if marker.lower() in content.lower():
                        found.append(marker)
                        continue
                except (FileNotFoundError, PermissionError):
                    pass

            # Check package.json
            pkg_file = self.project_path / "package.json"
            if pkg_file.exists():
                try:
                    content = pkg_file.read_text()
                    if marker in content:
                        found.append(marker)
                        continue
                except (FileNotFoundError, PermissionError):
                    pass

            # Check go.mod
            go_mod = self.project_path / "go.mod"
            if go_mod.exists():
                try:
                    content = go_mod.read_text()
                    if marker in content:
                        found.append(marker)
                        continue
                except (FileNotFoundError, PermissionError):
                    pass

            # Check Cargo.toml
            cargo = self.project_path / "Cargo.toml"
            if cargo.exists():
                try:
                    content = cargo.read_text()
                    if marker in content:
                        found.append(marker)
                        continue
                except (FileNotFoundError, PermissionError):
                    pass
        return found
