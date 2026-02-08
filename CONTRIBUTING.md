# Contributing to Video Processor

Thank you for your interest in contributing to Video Processor! This document provides guidelines and instructions for contributing to the project.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Title**: A clear and descriptive title
- **Description**: A detailed description of the problem
- **Steps to Reproduce**: Steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS and version
  - Python version
  - FFmpeg version
  - Video Processor version
- **Screenshots/Logs**: If applicable, include screenshots and log files
- **Additional Context**: Any other relevant information

### Suggesting Enhancements

Feature suggestions are welcome! When suggesting a new feature:

- **Title**: A clear and descriptive title
- **Description**: A detailed description of the feature
- **Motivation**: Why would this feature be useful?
- **Use Cases**: Specific use cases for the feature
- **Alternatives**: Any alternatives you've considered
- **Additional Context**: Any other relevant information

### Pull Requests

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/video-processor.git
   cd video-processor
   ```

2. **Create a Branch**
   ```bash
   # Create a feature branch
   git checkout -b feature/amazing-feature
   # Or a bugfix branch
   git checkout -b fix/issue-123
   ```

3. **Make Your Changes**
   - Write clear, concise code
   - Add comments for complex logic
   - Follow the existing code style
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run all tests
   python -m unittest

   # Run specific test files
   python -m unittest tests.test_ffmpeg
   python -m unittest tests.test_config
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Use [conventional commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Test changes
   - `chore:` Build process or auxiliary tool changes

6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Link related issues
   - Request reviews

## Code Style

### Python Style Guide

We follow PEP 8 style guidelines. Recommended tools:

```bash
# Install linters and formatters
uv pip install ruff black isort mypy

# Format code
black src/ tests/
isort src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (optional)
mypy src/
```

### Code Organization

- Keep functions focused and small
- Use descriptive variable and function names
- Add docstrings for public functions and classes
- Group related functions together
- Follow the existing directory structure

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update REQUIREMENTS.md for requirement changes
- Add inline comments for complex logic

## Development Workflow

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/video-processor.git
cd video-processor

# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install in development mode
uv pip install -e .

# Install development tools
uv pip install ruff black isort mypy pytest
```

### Running Tests

```bash
# Run all tests
python -m unittest

# Run specific test file
python -m unittest tests.test_ffmpeg

# Run with verbose output
python -m unittest -v

# Run specific test
python -m unittest tests.test_ffmpeg.TestFFmpeg.test_video_info
```

### Running the Application

```bash
# GUI mode
video-processor-gui

# CLI mode
video-processor --input "C:\Videos" --output "C:\Optimized"
```

## Guidelines

### Do's

- Write clear, readable code
- Add tests for new features
- Update documentation
- Follow existing code style
- Be respectful and constructive in discussions
- Test your changes thoroughly

### Don'ts

- Don't commit without testing
- Don't break existing tests without a good reason
- Don't add dependencies without discussion
- Don't leave commented-out code in the repository
- Don't commit sensitive information

## Project Structure

```
video-processor/
├── src/
│   └── video_processor/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Configuration management
│       ├── engine.py           # Processing engine
│       ├── ffmpeg.py           # FFmpeg wrapper
│       ├── logging.py          # Logging utilities
│       └── gui/                # GUI components
│           ├── __init__.py
│           ├── app.py          # Main application
│           ├── theme.py        # Theme management
│           ├── settings_view.py
│           ├── extensions_view.py
│           ├── progress_view.py
│           └── models.py       # Data models
├── tests/
│   ├── test_ffmpeg.py
│   └── test_config.py
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── REQUIREMENTS.md
```

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussions
- **Documentation**: Check README.md and REQUIREMENTS.md

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Respect different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory language
- Personal attacks or derogatory comments
- Public or private harassment
- Publishing others' private information without permission
- Other unethical or unprofessional conduct

### Reporting Issues

If you encounter unacceptable behavior, please report it to the project maintainers through private communication.

## Recognition

Contributors will be recognized in:
- The CONTRIBUTORS.md file
- Release notes for significant contributions
- The project's website/documentation

Thank you for contributing to Video Processor! 🚀
