# Contributing to EnvForge 🤝

Thank you for your interest in contributing to EnvForge! This document provides guidelines for contributing.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/gitstq/EnvForge.git
cd EnvForge

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v
```

## Contribution Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints where possible
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat: add new feature`
- `fix: fix a bug`
- `docs: update documentation`
- `refactor: code refactoring`
- `test: add or update tests`
- `chore: maintenance tasks`

### Pull Request Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit with conventional commit message
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Reporting Issues
When reporting issues, please include:
- OS and Python version
- EnvForge version (`envforge --version`)
- Steps to reproduce
- Expected vs actual behavior
- Error output (if any)

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
