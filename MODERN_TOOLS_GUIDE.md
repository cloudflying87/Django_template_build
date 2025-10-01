# Modern Development Tools Guide

This template uses cutting-edge Python development tools for maximum speed and efficiency.

## 🚀 UV - Ultra-Fast Package Manager

**Why UV?** 10-100x faster than pip, written in Rust.

### Installation
```bash
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Usage (drop-in pip replacement)
```bash
# Instead of: pip install -r requirements.txt
uv pip install -r requirements.txt

# Instead of: pip install django
uv pip install django

# Instead of: pip install --upgrade package
uv pip install --upgrade package
```

### Speed Comparison
- **pip**: ~45 seconds to install Django project dependencies
- **uv**: ~2-5 seconds for the same dependencies (90% faster!)

### The Makefile handles this automatically
```bash
make install  # Automatically uses uv if available, falls back to pip
```

---

## 🔧 Ruff - Ultra-Fast Linter & Formatter

**Replaces**: Black, isort, flake8, pyupgrade, and more!

**Why Ruff?** 10-100x faster than traditional tools, written in Rust.

### What It Does
- **Linting**: Catches bugs, style issues, security problems
- **Formatting**: Auto-formats code like Black
- **Import sorting**: Organizes imports like isort
- **Auto-fixing**: Fixes many issues automatically

### Usage
```bash
# Format code
make format
# or
ruff format .
ruff check --fix .

# Check code quality
make lint
# or
ruff check .
ruff format --check .
```

### Configuration
See `pyproject.toml` for all rules and settings.

### Rules Enabled
- **E, W**: PEP 8 style
- **F**: PyFlakes (catch bugs)
- **I**: Import sorting
- **B**: Bugbear (catch common bugs)
- **S**: Security checks
- **DJ**: Django-specific checks
- **UP**: Modern Python syntax

---

## 🔍 Mypy - Type Checking

**Why Mypy?** Catch bugs before runtime with static type analysis.

### Usage
```bash
make type-check
# or
mypy apps/ config/
```

### Example
```python
# Bad - will catch type errors
def get_user(id: int) -> User:
    return User.objects.get(id=id)

result = get_user("123")  # mypy error: Expected int, got str
```

### Configuration
See `pyproject.toml` for mypy settings.

---

## 🛡️ Bandit - Security Scanner

**Why Bandit?** Automatically find security vulnerabilities.

### Usage
```bash
make security
# or
bandit -r apps/ -c pyproject.toml
```

### What It Catches
- SQL injection vulnerabilities
- Hardcoded passwords
- Use of insecure functions
- Command injection risks
- And much more!

---

## 🪝 Pre-commit Hooks

Automatically run checks before every commit.

### Setup
```bash
make setup  # Installs pre-commit hooks automatically
# or
pre-commit install
```

### What Runs on Every Commit
1. **Ruff** - Format and lint
2. **Mypy** - Type checking
3. **Bandit** - Security scan
4. **django-upgrade** - Modernize Django code
5. **File checks** - Trailing whitespace, large files, secrets
6. **Template formatting** - Django HTML templates
7. **Dockerfile linting** - Best practices

### Manual Run
```bash
pre-commit run --all-files
```

### Skip Hooks (when needed)
```bash
git commit --no-verify -m "Emergency fix"
```

---

## 🧪 Pytest - Modern Testing

**Why Pytest?** More powerful and easier than Django's test framework.

### Usage
```bash
make test
# or
pytest

# With coverage
make coverage
# or
pytest --cov --cov-report=html
```

### Features Configured
- **pytest-django**: Django integration
- **pytest-cov**: Code coverage
- **pytest-xdist**: Parallel test execution
- **factory-boy**: Test data factories
- **faker**: Realistic fake data

### Example Test
```python
import pytest
from apps.core.models import User

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(
        username='test',
        email='test@example.com'
    )
    assert user.username == 'test'
    assert user.email == 'test@example.com'
```

---

## 📊 GitHub Actions - CI/CD

Automated checks on every push and pull request.

### Workflows Included

#### 1. CI Workflow (`.github/workflows/ci.yml`)
Runs on every push/PR:
- ✅ Ruff linting and formatting
- ✅ Mypy type checking
- ✅ Security scanning with Bandit
- ✅ Full test suite with coverage
- ✅ Docker build test
- ✅ Coverage reporting to Codecov

#### 2. CodeQL Security (`.github/workflows/codeql.yml`)
- Weekly security scans
- Advanced vulnerability detection
- Automatic security alerts

#### 3. Dependency Review (`.github/workflows/dependency-review.yml`)
- Checks for vulnerable dependencies on PRs
- Prevents introducing known CVEs

### Setup
1. Push code to GitHub
2. Workflows run automatically
3. Get email alerts on failures
4. See results in PR checks

### Local Testing (before pushing)
```bash
# Run what CI runs
make quality    # Lint + type-check + security
make test       # Run tests
make docker-build  # Test Docker build
```

---

## 📈 Speed Improvements

### Before (Old Tools)
```
pip install -r requirements.txt     → 45 seconds
black + isort + flake8              → 12 seconds
Running tests                       → 8 seconds
Docker build                        → 3 minutes

Total development cycle: ~4 minutes
```

### After (Modern Tools)
```
uv pip install -r requirements.txt  → 3 seconds (93% faster!)
ruff format + check                 → 0.5 seconds (96% faster!)
pytest with xdist                   → 4 seconds (50% faster!)
Docker build (cached)               → 30 seconds (83% faster!)

Total development cycle: ~40 seconds (83% faster overall!)
```

---

## 🎯 Quick Commands Reference

### Development
```bash
make run          # Start dev server
make shell        # Django shell
make migrate      # Run migrations
```

### Code Quality
```bash
make format       # Auto-format code (ruff)
make lint         # Check code quality (ruff)
make type-check   # Type checking (mypy)
make security     # Security scan (bandit)
make quality      # Run all checks
```

### Testing
```bash
make test         # Run tests
make coverage     # Tests with coverage report
```

### Dependencies
```bash
make install-uv   # Install UV package manager
make install      # Install all dependencies (uses UV if available)
```

### Docker/Production
```bash
make docker-build # Build containers
make deploy       # Deploy with backup
make backup       # Backup database
```

---

## 🆚 Tool Comparison

| Task | Old Tool | New Tool | Speed Improvement |
|------|----------|----------|-------------------|
| Package install | pip | uv | 10-100x faster |
| Code formatting | black | ruff format | 100x faster |
| Import sorting | isort | ruff (built-in) | 100x faster |
| Linting | flake8 | ruff check | 100x faster |
| All quality checks | Combined | ruff + mypy | 50x faster |

---

## 💡 Pro Tips

### 1. Use UV for Everything
```bash
# Instead of pip
alias pip="uv pip"

# Add to ~/.bashrc or ~/.zshrc
echo 'alias pip="uv pip"' >> ~/.bashrc
```

### 2. Auto-format on Save (VS Code)
Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  }
}
```

### 3. Parallel Testing
```bash
# Use all CPU cores
pytest -n auto

# Or specific number
pytest -n 4
```

### 4. Watch Mode for Tests
```bash
# Install pytest-watch
uv pip install pytest-watch

# Auto-run tests on file changes
ptw
```

---

## 🔗 Learn More

- **UV**: https://github.com/astral-sh/uv
- **Ruff**: https://github.com/astral-sh/ruff
- **Mypy**: https://mypy.readthedocs.io/
- **Bandit**: https://bandit.readthedocs.io/
- **Pre-commit**: https://pre-commit.com/
- **Pytest**: https://docs.pytest.org/

---

## 🚨 Troubleshooting

### UV not found
```bash
# Install UV
pip install uv

# Or use curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Pre-commit hooks failing
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Run manually to see errors
pre-commit run --all-files
```

### Ruff errors after upgrade
```bash
# Auto-fix what can be fixed
ruff check --fix .

# Then manually fix remaining issues
ruff check .
```

### Type checking errors
```bash
# Ignore specific errors (use sparingly)
variable = some_function()  # type: ignore

# Better: Add proper type hints
def some_function() -> str:
    return "result"
```
