# Contributing to Personal Assistant

Thank you for your interest in contributing to the Personal Assistant project! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/personal-assistant.git
   cd personal-assistant
   ```
3. Set up the development environment:
   ```bash
   ./setup.sh  # On Windows: setup.bat
   ```
4. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused on a single responsibility

### Adding New Features

1. **New Assistant Functions**:
   - Add new function tools to the appropriate assistant file
   - Follow the existing pattern for function tools
   - Update the assistant's instructions to include the new functionality

2. **New Integrations**:
   - Create a new file in the `integrations` directory
   - Follow the pattern of existing integrations
   - Update `setup_integrations.py` to include the new integration
   - Update `integrated_assistant.py` to use the new integration

### Testing

Before submitting a pull request, make sure to:

1. Test your changes with the test script:
   ```bash
   ./test_integrated_assistant.py
   ```
2. Test the assistant in all modes:
   ```bash
   ./run.py --mode basic
   ./run.py --mode advanced
   ./run.py --mode web
   ./run.py --mode integrated
   ```

## Pull Request Process

1. Update the README.md and other documentation with details of changes
2. Update the requirements.txt file if you've added new dependencies
3. Make sure all tests pass
4. Submit a pull request with a clear description of the changes

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License. 