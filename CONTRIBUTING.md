# Contributing to Ottoke 🚀

First off, thank you for considering contributing to Ottoke! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

All types of contributions are welcome: bug reports, documentation improvements, feature requests, and code contributions.

---

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Local Development Setup](#local-development-setup)
- [Git Workflow & Branching Guidelines](#git-workflow--branching-guidelines)
- [Commit Message Style Guide](#commit-message-style-guide)
- [Code Standards](#code-standards)

---

## Code of Conduct

We aim to foster an open and welcoming environment. Please be respectful, constructive, and collaborative in all communication (issues, PRs, comments).

---

## How Can I Contribute?

### Reporting Bugs
If you find a bug:
1. Search the existing issues to ensure it hasn't already been reported.
2. Open a new issue with a clear title and description, including:
   * Steps to reproduce the bug.
   * Expected vs. actual behavior.
   * Screenshots (if applicable).
   * Your operating system and environment (Docker, local python, K8s, etc.).

### Suggesting Enhancements
We welcome new feature ideas!
1. Search existing issues to see if the feature has already been suggested.
2. Open an issue describing:
   * The problem this feature solves.
   * The proposed implementation or user flow.
   * Alternatives considered.

### Pull Requests
Ready to contribute code? Follow these steps:
1. Fork the repository and clone it locally.
2. Create a new branch from `main` (see branching guidelines below).
3. Implement your changes, keeping them focused and minimal.
4. Test your changes locally (both Docker Compose and Kubernetes if applicable).
5. Commit and push your changes to your fork.
6. Open a Pull Request against the `main` branch of the original repository.

---

## Local Development Setup

To set up your environment, see the **Local Development** section in the [README.md](file:///c:/Users/hriti/project/Ottoke/README.md).

### Python Virtual Env
Ensure your virtual environment is active and dev dependencies are installed:
```bash
python -m venv venv
# Activate virtualenv (see README for OS-specific commands)
pip install -r requirements.txt
```

---

## Git Workflow & Branching Guidelines

We follow a branch-and-merge workflow. Please name your branches using the following conventions:

*   `feature/your-feature-name` for new features or enhancements.
*   `bugfix/issue-description` for bug fixes.
*   `docs/documentation-update` for documentation changes.
*   `chore/maintenance-work` for CI/CD updates, dependency upgrades, etc.

Always create your branch from the latest `main` branch:
```bash
git checkout main
git pull origin main
git checkout -b feature/cool-new-feature
```

---

## Commit Message Style Guide

We follow semantic commit messages to keep our git history clean and readable:

*   `feat`: A new feature (e.g., `feat: add rate limiting to comments`)
*   `fix`: A bug fix (e.g., `fix: resolve connection timeout to postgres`)
*   `docs`: Documentation changes (e.g., `docs: update deployment instructions`)
*   `style`: Formatting, missing semi-colons, etc. (no code change)
*   `refactor`: Code changes that neither fix a bug nor add a feature
*   `test`: Adding missing tests or correcting existing tests
*   `chore`: Maintenance tasks, dependencies, helper scripts (e.g., `chore: update requirements.txt`)

*Example commit message:*
```text
feat: integrate Redis cache for high-frequency IP rate limits
```

---

## Code Standards

*   **Backend (Python)**:
    *   Follow **PEP 8** style guidelines.
    *   Keep functions focused, concise, and well-documented.
    *   Use parameterized queries in database calls (`%s` for PostgreSQL, `?` for SQLite) to prevent SQL injection.
*   **Frontend (HTML/JS/CSS)**:
    *   Write clean, vanilla CSS and semantic HTML5.
    *   Ensure designs are fully responsive (test on mobile and desktop viewports).
    *   Escape all user inputs before printing to DOM to prevent Cross-Site Scripting (XSS).
*   **Kubernetes & Helm**:
    *   Always parameterize dynamic values in Helm templates.
    *   Maintain resource request/limit constraints for deployments to ensure cluster stability.
