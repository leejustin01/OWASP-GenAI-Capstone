# Contributing Guide

How to set up, code, test, review, and release so contributions meet our Definition of Done.

## Code of Conduct

- Treat all team members and community members respectfully
- Be open to feedback and constructive criticism
- Contribute thoughtful and relevant code
- Report violations of the Code of Conduct to team members via email


## Getting Started

Follow these steps to set up your development environment and run the project locally.

### Prerequisites

- Python 3.10 or higher
- Git
- Access to the repository
- Any required environment variables or secrets

### Setup

```bash
git clone https://github.com/leejustin01/OWASP-GenAI-Capstone.git
git checkout <Your-Name>
cd OWASP-GenAI-Capstone/owaspTop10/<vulnerability>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables / Secrets
- Store secrets in .env
- Do not commit secrets or .env to the repo

### Running locally

```bash
python app.py
```

## Branching & Workflow



### Default Branch
- main is the default branch
- It always contains stable, reviewed code

### Team Member Branches
- Each team member has their own persistent branch for development
    - Justin
    - Jackson
    - Amit
    - Ohm
    - Jared
- All work is committed to personal branches

### Workflow
1. Code on your branch
    - Make changes locally, following clean code guidelines
2. Push to your branch
    - Keep your branch up-to-date with main
3. Open pull requests to merge your branch into main
    - Submit a PR for review and CI checks

## Issues & Planning

### Filing issues
- Use GitHub Issues templates
- Labels: bug, feature, enhancement, documentation, security
- Include description, reproduction steps, and expected behavior
- Team members assign issues during planned meetings


## Commit Messages

Follow Conventional Commits Format:

```bash
feat: add submit button
fix: resolved page not found error
docs: updated README.md
```

## Code Style, Linting & Formatting

Name the formatter/linter, config file locations, and the exact commands to check/fix locally.

### Linter - Ruff
Command to check locally:
```bash
ruff check .
```

### Type Checker - Mypy
Command to check locally:
```bash
mypy .
```

### Before pushing, ensure checks pass locally.

## Testing

Due to the individual nature of this project, a consensus has not yet been reached on testing between our team and project partner.

## Pull Requests & Reviews

### Requirements
- Use the PR template
- Keep PRs small (under 400 lines)
- Link related issues

### Reviewer Expectations
- Check code quality, style, and "smell"
- Approve only if all requirements are met

### Approval rules
- At least 1 team member must approve
- CI must pass before merge

### Required Status Checks
- Linting and Type Checking

## CI/CD

### Pipeline
- Defined in .github/workflows/
- Mandatory jobs:
    - Code Quality Check - Ruff and Mypy
- Viewing Logs: GitHub Actions -> Workflow

## Security & Secrets

- Vulnerability reporting: email team members
- Prohibited patterns: hard-coded credentials, API keys, or secrets
- Dependency update policy: use Dependabot and review before merging
- Scanning tools: CI runs linting and type checking


## Documentation Expectations

Specify what must be updated (README, docs/, API refs, CHANGELOG) and docstring/comment standards.

The following documentation must be updated with relevant information regarding your changes:
- README.md
- API references
- Code comments


## Release Process

Releases are not yet applicable to our project.

## Support & Contact

### Team members:
- Justin Lee
- Ohm Thakor
- Jackson Miller
- Amit Guha
- Jared Yin

### Contact channel: Email or GitHub issues
### Response window: 24-48 hours
### Questions: Email team members or GitHub issues with the 'question' tag

