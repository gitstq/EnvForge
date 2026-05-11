"""
Configuration generator - generates standardized environment configuration
files based on detected tech stack.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ConfigGenerator:
    """Generates standardized environment configuration files."""

    def __init__(self, snapshot: dict, output_dir: str = "."):
        self.snapshot = snapshot
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> Dict[str, str]:
        """Generate all applicable configuration files."""
        generated = {}

        # Always generate envforge snapshot
        generated["envforge.snapshot.json"] = self._generate_snapshot_file()

        # Generate .env.example based on detected frameworks
        env_content = self._generate_env_example()
        if env_content:
            generated[".env.example"] = env_content

        # Generate Dockerfile based on detected languages
        dockerfile = self._generate_dockerfile()
        if dockerfile:
            generated["Dockerfile"] = dockerfile

        # Generate docker-compose.yml
        compose = self._generate_docker_compose()
        if compose:
            generated["docker-compose.yml"] = compose

        # Generate .tool-versions (asdf format)
        tool_versions = self._generate_tool_versions()
        if tool_versions:
            generated[".tool-versions"] = tool_versions

        # Generate Makefile
        makefile = self._generate_makefile()
        if makefile:
            generated["Makefile"] = makefile

        # Generate .gitignore
        gitignore = self._generate_gitignore()
        if gitignore:
            generated[".gitignore"] = gitignore

        # Generate devcontainer.json
        devcontainer = self._generate_devcontainer()
        if devcontainer:
            generated[".devcontainer/devcontainer.json"] = devcontainer

        return generated

    def _generate_snapshot_file(self) -> str:
        """Generate the envforge snapshot JSON file."""
        snapshot_data = {
            "schema_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "project_path": self.snapshot.get("project_path", ""),
            "os_info": self.snapshot.get("os_info", {}),
            "languages": self.snapshot.get("languages", []),
            "frameworks": self.snapshot.get("frameworks", []),
            "package_managers": self.snapshot.get("package_managers", []),
            "tools": self.snapshot.get("tools", {}),
            "config_files": self.snapshot.get("config_files", []),
            "dependencies": self.snapshot.get("dependencies", {}),
        }
        return json.dumps(snapshot_data, indent=2, ensure_ascii=False)

    def _generate_env_example(self) -> str:
        """Generate .env.example based on detected frameworks."""
        lines = ["# EnvForge - Auto-generated environment variables template",
                 f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                 "# Copy this file to .env and fill in the values",
                 ""]

        frameworks = [f["name"] for f in self.snapshot.get("frameworks", [])]
        languages = [l["name"] for l in self.snapshot.get("languages", [])]

        # Common variables
        lines.extend([
            "# === Application ===",
            "APP_NAME=my-app",
            "APP_ENV=development",
            "APP_DEBUG=true",
            "APP_PORT=8000",
            "APP_HOST=0.0.0.0",
            "",
            "# === Logging ===",
            "LOG_LEVEL=DEBUG",
            "LOG_FORMAT=text",
            "",
        ])

        # Database variables
        if any(fw in frameworks for fw in ["Django", "Flask", "FastAPI", "Express", "Rails", "Laravel", "Spring Boot"]):
            lines.extend([
                "# === Database ===",
                "DATABASE_URL=postgresql://user:password@localhost:5432/mydb",
                "DATABASE_HOST=localhost",
                "DATABASE_PORT=5432",
                "DATABASE_NAME=mydb",
                "DATABASE_USER=user",
                "DATABASE_PASSWORD=password",
                "",
            ])

        # Redis
        if any(fw in frameworks for fw in ["Django", "FastAPI", "Express", "Laravel"]):
            lines.extend([
                "# === Redis ===",
                "REDIS_URL=redis://localhost:6379/0",
                "REDIS_HOST=localhost",
                "REDIS_PORT=6379",
                "",
            ])

        # Python specific
        if "Python" in languages:
            lines.extend([
                "# === Python ===",
                "PYTHONPATH=.",
                "PYTHONUNBUFFERED=1",
                "PYTHONDONTWRITEBYTECODE=1",
                "",
            ])

        # Node.js specific
        if "JavaScript" in languages or "TypeScript" in languages:
            lines.extend([
                "# === Node.js ===",
                "NODE_ENV=development",
                "PORT=3000",
                "",
            ])

        # AI/ML specific
        if any(fw in frameworks for fw in ["PyTorch", "TensorFlow", "Hugging Face", "LangChain"]):
            lines.extend([
                "# === AI/ML ===",
                "CUDA_VISIBLE_DEVICES=0",
                "MODEL_CACHE_DIR=./models",
                "HF_HOME=./cache/huggingface",
                "",
            ])

        # API keys placeholder
        lines.extend([
            "# === API Keys (fill in as needed) ===",
            "# API_KEY=your-api-key-here",
            "# SECRET_KEY=your-secret-key-here",
            "",
        ])

        return "\n".join(lines)

    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile based on detected languages."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        frameworks = [f["name"] for f in self.snapshot.get("frameworks", [])]

        if not languages:
            return ""

        primary_lang = languages[0]

        if primary_lang == "Python":
            return self._generate_python_dockerfile(frameworks)
        elif primary_lang in ("JavaScript", "TypeScript"):
            return self._generate_node_dockerfile(frameworks)
        elif primary_lang == "Go":
            return self._generate_go_dockerfile()
        elif primary_lang == "Rust":
            return self._generate_rust_dockerfile()
        elif primary_lang == "Java":
            return self._generate_java_dockerfile()
        elif primary_lang == "Ruby":
            return self._generate_ruby_dockerfile()
        elif primary_lang == "PHP":
            return self._generate_php_dockerfile()
        else:
            return self._generate_generic_dockerfile(primary_lang)

    def _generate_python_dockerfile(self, frameworks: List[str]) -> str:
        """Generate Python Dockerfile."""
        has_fastapi = "FastAPI" in frameworks
        has_django = "Django" in frameworks
        has_ml = any(fw in frameworks for fw in ["PyTorch", "TensorFlow", "Hugging Face"])

        if has_ml:
            base_image = "python:3.11-slim"
        else:
            base_image = "python:3.12-slim"

        lines = [
            f"FROM {base_image}",
            "",
            "WORKDIR /app",
            "",
            "# Install system dependencies",
            "RUN apt-get update && apt-get install -y --no-install-recommends \\",
            "    gcc \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
        ]

        # Copy dependency files
        pm_managers = self.snapshot.get("package_managers", [])
        pm_names = [pm["name"] for pm in pm_managers]

        if "poetry" in pm_names:
            lines.extend([
                "# Install Poetry",
                "RUN pip install --no-cache-dir poetry",
                "",
                "COPY pyproject.toml poetry.lock ./",
                "RUN poetry config virtualenvs.create false \\",
                "    && poetry install --no-dev --no-interaction --no-ansi",
                "",
            ])
        elif "uv" in pm_names:
            lines.extend([
                "# Install uv",
                "RUN pip install --no-cache-dir uv",
                "",
                "COPY pyproject.toml uv.lock ./",
                "RUN uv sync --frozen --no-dev",
                "",
            ])
        else:
            lines.extend([
                "COPY requirements.txt .",
                "RUN pip install --no-cache-dir -r requirements.txt",
                "",
            ])

        lines.extend([
            "# Copy application code",
            "COPY . .",
            "",
        ])

        if has_fastapi:
            lines.extend([
                'EXPOSE 8000',
                'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]',
            ])
        elif has_django:
            lines.extend([
                'EXPOSE 8000',
                'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]',
            ])
        else:
            lines.extend([
                'CMD ["python", "main.py"]',
            ])

        return "\n".join(lines)

    def _generate_node_dockerfile(self, frameworks: List[str]) -> str:
        """Generate Node.js Dockerfile."""
        has_next = "Next.js" in frameworks
        has_nuxt = "Nuxt" in frameworks

        if has_next:
            lines = [
                "FROM node:20-alpine AS deps",
                "WORKDIR /app",
                "COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./",
                "RUN npm ci --ignore-scripts",
                "",
                "FROM node:20-alpine AS builder",
                "WORKDIR /app",
                "COPY --from=deps /app/node_modules ./node_modules",
                "COPY . .",
                "RUN npm run build",
                "",
                "FROM node:20-alpine AS runner",
                "WORKDIR /app",
                "ENV NODE_ENV=production",
                "COPY --from=builder /app/.next/standalone ./",
                "COPY --from=builder /app/.next/static ./.next/static",
                "COPY --from=builder /app/public ./public",
                'EXPOSE 3000',
                'CMD ["node", "server.js"]',
            ]
        elif has_nuxt:
            lines = [
                "FROM node:20-alpine",
                "WORKDIR /app",
                "COPY package.json package-lock.json* ./",
                "RUN npm ci",
                "COPY . .",
                "RUN npm run build",
                'ENV HOST=0.0.0.0',
                'ENV PORT=3000',
                'EXPOSE 3000',
                'CMD ["node", ".output/server/index.mjs"]',
            ]
        else:
            lines = [
                "FROM node:20-alpine",
                "WORKDIR /app",
                "COPY package.json package-lock.json* ./",
                "RUN npm ci",
                "COPY . .",
                'EXPOSE 3000',
                'CMD ["npm", "start"]',
            ]

        return "\n".join(lines)

    def _generate_go_dockerfile(self) -> str:
        """Generate Go Dockerfile."""
        return "\n".join([
            "FROM golang:1.22-alpine AS builder",
            "WORKDIR /app",
            "COPY go.mod go.sum ./",
            "RUN go mod download",
            "COPY . .",
            'RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .',
            "",
            "FROM alpine:3.19",
            "WORKDIR /app",
            'COPY --from=builder /app/server .',
            'EXPOSE 8080',
            'CMD ["./server"]',
        ])

    def _generate_rust_dockerfile(self) -> str:
        """Generate Rust Dockerfile."""
        return "\n".join([
            "FROM rust:1.77-alpine AS builder",
            "WORKDIR /app",
            "RUN apk add --no-cache musl-dev",
            "COPY Cargo.toml Cargo.lock ./",
            "RUN mkdir src && echo 'fn main() {}' > src/main.rs",
            "RUN cargo build --release && rm -rf src",
            "COPY . .",
            "RUN touch src/main.rs && cargo build --release",
            "",
            "FROM alpine:3.19",
            "WORKDIR /app",
            'COPY --from=builder /app/target/release/app .',
            'EXPOSE 8080',
            'CMD ["./app"]',
        ])

    def _generate_java_dockerfile(self) -> str:
        """Generate Java Dockerfile."""
        return "\n".join([
            "FROM eclipse-temurin:21-jdk-alpine",
            "WORKDIR /app",
            "COPY pom.xml .",
            "COPY src ./src",
            "RUN ./mvnw clean package -DskipTests",
            'EXPOSE 8080',
            'CMD ["java", "-jar", "target/*.jar"]',
        ])

    def _generate_ruby_dockerfile(self) -> str:
        """Generate Ruby Dockerfile."""
        return "\n".join([
            "FROM ruby:3.3-alpine",
            "WORKDIR /app",
            "RUN apk add --no-cache build-base",
            "COPY Gemfile Gemfile.lock ./",
            "RUN bundle install --jobs 4 --retry 3",
            "COPY . .",
            'EXPOSE 3000',
            'CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "3000"]',
        ])

    def _generate_php_dockerfile(self) -> str:
        """Generate PHP Dockerfile."""
        return "\n".join([
            "FROM php:8.3-fpm-alpine",
            "WORKDIR /app",
            "RUN apk add --no-cache $PHPIZE_DEPS",
            "COPY composer.json composer.lock ./",
            "RUN composer install --no-dev --optimize-autoloader",
            "COPY . .",
        ])

    def _generate_generic_dockerfile(self, lang: str) -> str:
        """Generate generic Dockerfile."""
        return "\n".join([
            "FROM alpine:3.19",
            "WORKDIR /app",
            "COPY . .",
            'CMD ["sh", "-c", "echo \'Please customize the Dockerfile for your project\'"]',
        ])

    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        frameworks = [f["name"] for f in self.snapshot.get("frameworks", [])]

        lines = [
            "# EnvForge - Auto-generated Docker Compose configuration",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "version: '3.8'",
            "",
            "services:",
            "  app:",
            "    build: .",
            "    ports:",
        ]

        if "Python" in languages:
            lines.append('      - "8000:8000"')
        elif "JavaScript" in languages or "TypeScript" in languages:
            lines.append('      - "3000:3000"')
        elif "Go" in languages or "Rust" in languages:
            lines.append('      - "8080:8080"')
        else:
            lines.append('      - "8000:8000"')

        lines.extend([
            "    volumes:",
            '      - ".:/app"',
            "    environment:",
            '      - APP_ENV=development',
        ])

        # Add database services for web frameworks
        if any(fw in frameworks for fw in ["Django", "Flask", "FastAPI", "Express", "Rails", "Laravel", "Spring Boot"]):
            lines.extend([
                "",
                "  db:",
                "    image: postgres:16-alpine",
                "    ports:",
                '      - "5432:5432"',
                "    environment:",
                '      POSTGRES_DB: mydb',
                '      POSTGRES_USER: user',
                '      POSTGRES_PASSWORD: password',
                "    volumes:",
                '      - postgres_data:/var/lib/postgresql/data',
            ])

        if any(fw in frameworks for fw in ["Django", "FastAPI", "Express", "Laravel"]):
            lines.extend([
                "",
                "  redis:",
                "    image: redis:7-alpine",
                "    ports:",
                '      - "6379:6379"',
            ])

        lines.extend([
            "",
            "volumes:",
            "  postgres_data:",
        ])

        return "\n".join(lines)

    def _generate_tool_versions(self) -> str:
        """Generate .tool-versions file for asdf."""
        lines = ["# EnvForge - Auto-generated tool versions",
                 f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]

        tools = self.snapshot.get("tools", {})
        languages = [l["name"] for l in self.snapshot.get("languages", [])]

        tool_mapping = {
            "python3": "python",
            "node": "nodejs",
            "go": "golang",
            "rustc": "rust",
            "ruby": "ruby",
            "java": "java",
        }

        for tool_key, asdf_name in tool_mapping.items():
            if tool_key in tools:
                version = tools[tool_key].strip()
                # Extract version number
                import re
                match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version)
                if match:
                    lines.append(f"{asdf_name} {match.group(1)}")

        return "\n".join(lines) if len(lines) > 3 else ""

    def _generate_makefile(self) -> str:
        """Generate Makefile with common development commands."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]
        frameworks = [f["name"] for f in self.snapshot.get("frameworks", [])]

        lines = [
            "# EnvForge - Auto-generated Makefile",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ".PHONY: help install dev build test lint clean docker-up docker-down",
            "",
            "help: ## Show this help",
            "\t@echo 'Usage: make [target]'",
            "\t@echo ''",
            "\t@echo 'Targets:'",
            "\t@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## / {printf \"  \\033[36m%-15s\\033[0m %s\\n\", $$1, $$2}' $(MAKEFILE_LIST)",
            "",
        ]

        if "Python" in languages:
            pm_names = [pm["name"] for pm in self.snapshot.get("package_managers", [])]
            if "poetry" in pm_names:
                lines.extend([
                    "install: ## Install dependencies",
                    "\tpoetry install",
                    "",
                    "dev: ## Run development server",
                    "\tpoetry run python main.py",
                    "",
                    "test: ## Run tests",
                    "\tpoetry run pytest",
                    "",
                    "lint: ## Run linter",
                    "\tpoetry run ruff check .",
                    "",
                ])
            elif "uv" in pm_names:
                lines.extend([
                    "install: ## Install dependencies",
                    "\tuv sync",
                    "",
                    "dev: ## Run development server",
                    "\tuv run python main.py",
                    "",
                    "test: ## Run tests",
                    "\tuv run pytest",
                    "",
                    "lint: ## Run linter",
                    "\tuv run ruff check .",
                    "",
                ])
            else:
                lines.extend([
                    "install: ## Install dependencies",
                    "\tpip install -r requirements.txt",
                    "",
                    "dev: ## Run development server",
                    "\tpython main.py",
                    "",
                    "test: ## Run tests",
                    "\tpytest",
                    "",
                    "lint: ## Run linter",
                    "\truff check .",
                    "",
                ])

        elif "JavaScript" in languages or "TypeScript" in languages:
            lines.extend([
                "install: ## Install dependencies",
                "\tnpm install",
                "",
                "dev: ## Run development server",
                "\tnpm run dev",
                "",
                "build: ## Build for production",
                "\tnpm run build",
                "",
                "test: ## Run tests",
                "\tnpm test",
                "",
                "lint: ## Run linter",
                "\tnpm run lint",
                "",
            ])

        elif "Go" in languages:
            lines.extend([
                "install: ## Install dependencies",
                "\tgo mod download",
                "",
                "dev: ## Run development server",
                "\tgo run .",
                "",
                "build: ## Build binary",
                "\tgo build -o bin/app .",
                "",
                "test: ## Run tests",
                "\tgo test ./...",
                "",
                "lint: ## Run linter",
                "\tgolangci-lint run",
                "",
            ])

        elif "Rust" in languages:
            lines.extend([
                "dev: ## Run development server",
                "\tcargo run",
                "",
                "build: ## Build release binary",
                "\tcargo build --release",
                "",
                "test: ## Run tests",
                "\tcargo test",
                "",
                "lint: ## Run linter",
                "\tcargo clippy",
                "",
            ])

        lines.extend([
            "docker-up: ## Start Docker services",
            "\tdocker-compose up -d",
            "",
            "docker-down: ## Stop Docker services",
            "\tdocker-compose down",
            "",
            "clean: ## Clean build artifacts",
            "\trm -rf dist/ build/ __pycache__ .pytest_cache node_modules target",
        ])

        return "\n".join(lines)

    def _generate_gitignore(self) -> str:
        """Generate .gitignore based on detected languages."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]

        lines = [
            "# EnvForge - Auto-generated .gitignore",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# === Environment ===",
            ".env",
            ".env.local",
            ".env.*.local",
            "",
            "# === OS ===",
            ".DS_Store",
            "Thumbs.db",
            "*.swp",
            "*.swo",
            "*~",
            "",
            "# === IDE ===",
            ".idea/",
            ".vscode/settings.json",
            ".vscode/launch.json",
            "*.iml",
            "",
        ]

        if "Python" in languages:
            lines.extend([
                "# === Python ===",
                "__pycache__/",
                "*.py[cod]",
                "*$py.class",
                "*.so",
                ".Python",
                "build/",
                "develop-eggs/",
                "dist/",
                "downloads/",
                "eggs/",
                ".eggs/",
                "lib/",
                "lib64/",
                "parts/",
                "sdist/",
                "var/",
                "wheels/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg",
                ".venv/",
                "venv/",
                ".tox/",
                ".mypy_cache/",
                ".pytest_cache/",
                ".ruff_cache/",
                "htmlcov/",
                ".coverage",
                ".coverage.*",
                "",
            ])

        if "JavaScript" in languages or "TypeScript" in languages:
            lines.extend([
                "# === Node.js ===",
                "node_modules/",
                "npm-debug.log*",
                "yarn-debug.log*",
                "yarn-error.log*",
                "pnpm-debug.log*",
                ".next/",
                ".nuxt/",
                "dist/",
                ".tsbuildinfo",
                "",
            ])

        if "Go" in languages:
            lines.extend([
                "# === Go ===",
                "bin/",
                "*.exe",
                "*.test",
                "*.out",
                "",
            ])

        if "Rust" in languages:
            lines.extend([
                "# === Rust ===",
                "target/",
                "**/*.rs.bk",
                "",
            ])

        if "Java" in languages:
            lines.extend([
                "# === Java ===",
                "*.class",
                "*.jar",
                "*.war",
                "*.ear",
                ".gradle/",
                "",
            ])

        lines.extend([
            "# === Docker ===",
            ".docker/",
            "",
            "# === EnvForge ===",
            "envforge.snapshot.json",
            ".env.example.bak",
        ])

        return "\n".join(lines)

    def _generate_devcontainer(self) -> str:
        """Generate devcontainer.json for VS Code Remote Containers."""
        languages = [l["name"] for l in self.snapshot.get("languages", [])]

        if "Python" in languages:
            config = {
                "name": "EnvForge Development",
                "image": "mcr.microsoft.com/devcontainers/python:3.12",
                "features": {
                    "ghcr.io/devcontainers/features/git:1": {},
                    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
                },
                "postCreateCommand": "pip install -r requirements.txt",
                "customizations": {
                    "vscode": {
                        "extensions": [
                            "ms-python.python",
                            "ms-python.vscode-pylance",
                            "charliermarsh.ruff",
                        ]
                    }
                },
                "remoteUser": "vscode",
            }
        elif "JavaScript" in languages or "TypeScript" in languages:
            config = {
                "name": "EnvForge Development",
                "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
                "features": {
                    "ghcr.io/devcontainers/features/git:1": {},
                    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
                },
                "postCreateCommand": "npm install",
                "customizations": {
                    "vscode": {
                        "extensions": [
                            "dbaeumer.vscode-eslint",
                            "esbenp.prettier-vscode",
                        ]
                    }
                },
                "remoteUser": "node",
            }
        elif "Go" in languages:
            config = {
                "name": "EnvForge Development",
                "image": "mcr.microsoft.com/devcontainers/go:1.22",
                "features": {
                    "ghcr.io/devcontainers/features/git:1": {},
                },
                "postCreateCommand": "go mod download",
                "customizations": {
                    "vscode": {
                        "extensions": [
                            "golang.go",
                        ]
                    }
                },
                "remoteUser": "vscode",
            }
        else:
            return ""

        return json.dumps(config, indent=2)
