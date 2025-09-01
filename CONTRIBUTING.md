# Contributing to AI WellnessVision

Thank you for your interest in contributing to AI WellnessVision! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Standards](#development-standards)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment. By participating, you agree to uphold this standard.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-wellness-vision.git
   cd ai-wellness-vision
   ```
3. **Set up the development environment** (see Development Setup below)
4. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or conda for package management
- Git for version control

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Start the API server**:
   ```bash
   python -m uvicorn src.api.gateway:app --reload
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues in the codebase
- **Feature additions**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance improvements**: Optimize existing code
- **Security enhancements**: Improve security measures

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** to discuss major changes before implementing them
3. **Follow the coding standards** outlined below
4. **Ensure your changes don't break existing functionality**

## Pull Request Process

1. **Update documentation** if your changes affect the API or user interface
2. **Add tests** for new functionality
3. **Ensure all tests pass**:
   ```bash
   pytest
   ```
4. **Update the README.md** if needed
5. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Error messages** or logs

### Feature Requests

For feature requests, please provide:

- **Clear description** of the proposed feature
- **Use case** and motivation
- **Possible implementation** approach
- **Alternative solutions** considered

## Development Standards

### Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

### Testing

- Write **unit tests** for new functionality
- Maintain **high test coverage** (aim for >80%)
- Include **integration tests** for complex features
- Use **pytest** for testing framework
- Mock external dependencies in tests

### Documentation

- Update **docstrings** for any changed functions
- Add **inline comments** for complex logic
- Update **README.md** for significant changes
- Include **examples** in documentation

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add voice recognition for multilingual support

- Implement Whisper integration for speech-to-text
- Add support for 7 languages including Indic languages
- Include audio preprocessing and validation
- Add comprehensive tests for speech functionality

Fixes #123
```

### Commit Message Format

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Security Considerations

- **Never commit** sensitive information (API keys, passwords, etc.)
- **Validate all inputs** in new functions
- **Follow security best practices** for health data handling
- **Report security vulnerabilities** privately to maintainers

### Performance Guidelines

- **Profile code** for performance-critical sections
- **Use appropriate data structures** and algorithms
- **Minimize memory usage** for large datasets
- **Cache results** where appropriate
- **Consider async/await** for I/O operations

## Getting Help

If you need help with contributing:

1. **Check the documentation** in the `docs/` directory
2. **Look at existing code** for examples
3. **Ask questions** in GitHub issues
4. **Join discussions** in GitHub Discussions (if enabled)

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** section

## Development Workflow

### Typical Workflow

1. **Sync your fork** with the main repository
2. **Create a feature branch** from `main`
3. **Make your changes** following the guidelines
4. **Test thoroughly** locally
5. **Commit with clear messages**
6. **Push to your fork**
7. **Create a pull request**
8. **Address review feedback**
9. **Merge after approval**

### Branch Naming

Use descriptive branch names:

- `feature/add-voice-recognition`
- `fix/image-upload-validation`
- `docs/update-api-documentation`
- `refactor/optimize-nlp-service`

## Questions?

If you have questions about contributing, please:

1. Check this document first
2. Look at existing issues and pull requests
3. Create a new issue with the "question" label
4. Contact the maintainers directly for sensitive matters

Thank you for contributing to AI WellnessVision! Your contributions help make healthcare AI more accessible and effective for everyone.