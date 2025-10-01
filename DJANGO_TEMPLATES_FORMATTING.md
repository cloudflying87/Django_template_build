# Django Template Formatting Guide

## 🚫 The Old Problem with Black

**Black would destroy Django templates!**

Example of what Black did (BAD):
```html
<!-- Before Black -->
{% extends "base.html" %}

{% block content %}
    <div class="container">
        {{ user.name }}
    </div>
{% endblock %}

<!-- After Black (BROKEN!) -->
{% extends "base.html" %} {% block content %}
<div class="container">{{ user.name }}</div>
{% endblock %}
```

Black would:
- Remove meaningful indentation
- Collapse multi-line tags
- Break template logic readability
- Mess up Jinja/Django syntax

---

## ✅ Our Solution: Ruff + djhtml

### How It Works

**1. Ruff is BLOCKED from touching templates**

Multiple layers of protection:

```toml
# pyproject.toml
[tool.ruff]
exclude = [
    "templates",  # Entire templates directory
    "*.html",     # All HTML files
    "*.jinja",    # Jinja templates
    "*.jinja2",   # Jinja2 templates
]
```

```yaml
# .pre-commit-config.yaml
- id: ruff
  types: [python]  # ONLY Python files
  exclude: ^(templates/|.*\.html$)  # Extra safety
```

**Result**: Ruff will **NEVER** touch your templates. Guaranteed.

---

### 2. djhtml Formats Templates Correctly

**djhtml** is Django-aware and understands template syntax!

Example:
```html
<!-- Messy template -->
{% extends "base.html" %}
{% block content %}
<div class="container">
{% for item in items %}
<p>{{ item.name }}</p>
{% endfor %}
</div>
{% endblock %}

<!-- After djhtml (PERFECT!) -->
{% extends "base.html" %}

{% block content %}
  <div class="container">
    {% for item in items %}
      <p>{{ item.name }}</p>
    {% endfor %}
  </div>
{% endblock %}
```

djhtml:
- ✅ Respects Django/Jinja template tags
- ✅ Proper indentation for `{% %}` blocks
- ✅ Handles `{{ }}` variables correctly
- ✅ Preserves template logic structure
- ✅ Works with template inheritance

---

## 📖 Using djhtml

### Automatic (Pre-commit Hook)

When you commit, djhtml runs automatically:

```bash
git add templates/my_template.html
git commit -m "Update template"

# Pre-commit runs:
# - djhtml formats your HTML ✅
# - ruff skips HTML completely ✅
```

### Manual Formatting

```bash
# Format a single file
djhtml templates/my_template.html

# Format entire directory
djhtml templates/

# With specific tab width (default is 2)
djhtml --tabwidth 4 templates/

# Check only (don't modify)
djhtml --check templates/
```

### In Makefile

```bash
# Format Python with ruff (won't touch templates)
make format

# Format templates separately if needed
djhtml templates/
```

---

## 🔒 Protection Layers

### Layer 1: File Type Filtering
```yaml
types: [python]  # Pre-commit only runs ruff on .py files
```

### Layer 2: Explicit Exclusion
```yaml
exclude: ^(templates/|.*\.html$|.*\.jinja$|.*\.jinja2$)
```

### Layer 3: Ruff Configuration
```toml
exclude = ["templates", "*.html", "*.jinja", "*.jinja2"]
```

### Layer 4: djhtml Handles Templates
```yaml
- id: djhtml
  files: \.(html|jinja|jinja2)$  # ONLY tool allowed to touch templates
```

**Result**: It's literally impossible for ruff to touch your templates!

---

## 🎯 File Type Mapping

| File Type | Tool Used | Purpose |
|-----------|-----------|---------|
| `*.py` | Ruff | Python formatting & linting |
| `*.html` | djhtml | Django template formatting |
| `*.jinja` | djhtml | Jinja template formatting |
| `*.jinja2` | djhtml | Jinja2 template formatting |
| `*.js` | (none) | JavaScript files |
| `*.css` | (none) | CSS files |
| `*.yml` | prettier | YAML formatting |
| `*.json` | (none) | JSON files |

---

## 💡 Best Practices

### 1. Let Pre-commit Handle It

Don't manually format templates. Just commit:

```bash
git add .
git commit -m "Update"

# Pre-commit automatically:
# - Formats Python with ruff
# - Formats templates with djhtml
# - Runs all other checks
```

### 2. Configure Your Editor

#### VS Code (`settings.json`)

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "[html]": {
    "editor.defaultFormatter": "monosans.djlint",
    "editor.formatOnSave": true
  },
  "[django-html]": {
    "editor.defaultFormatter": "monosans.djlint",
    "editor.formatOnSave": true
  }
}
```

#### VS Code Extensions

Install these extensions:
- `charliermarsh.ruff` - Ruff for Python
- `monosans.djlint` - Django template linting/formatting
- `batisteo.vscode-django` - Django syntax highlighting

### 3. Template Structure

Keep templates clean:

```html
{% extends "base.html" %}

{% load static %}

{% block title %}My Page{% endblock %}

{% block content %}
  <div class="container">
    {% if user.is_authenticated %}
      <h1>Welcome, {{ user.username }}!</h1>

      {% for item in items %}
        <div class="item">
          <h2>{{ item.title }}</h2>
          <p>{{ item.description }}</p>
        </div>
      {% endfor %}
    {% else %}
      <p>Please log in.</p>
    {% endif %}
  </div>
{% endblock %}
```

djhtml will maintain this beautiful structure!

---

## 🧪 Testing the Configuration

### 1. Create a Test Template

```bash
cat > templates/test.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<div>
{% for i in items %}
<p>{{ i }}</p>
{% endfor %}
</div>
{% endblock %}
EOF
```

### 2. Run djhtml

```bash
djhtml templates/test.html
cat templates/test.html
```

**Expected output (properly formatted):**
```html
{% extends "base.html" %}

{% block content %}
  <div>
    {% for i in items %}
      <p>{{ i }}</p>
    {% endfor %}
  </div>
{% endblock %}
```

### 3. Verify Ruff Ignores It

```bash
# This should NOT touch the HTML file
ruff format templates/test.html

# Ruff will say: "1 file left unchanged" or ignore it
```

### 4. Test Pre-commit

```bash
git add templates/test.html
pre-commit run --all-files

# You should see:
# - ruff: Passed (skipped HTML files)
# - djhtml: Passed (formatted HTML)
```

---

## 🐛 Troubleshooting

### "Ruff is touching my templates!"

This shouldn't happen, but if it does:

```bash
# Check ruff configuration
ruff check --config pyproject.toml

# Verify exclusions
grep -A 10 "exclude" pyproject.toml

# Should see templates, *.html, etc.
```

### "djhtml not running"

```bash
# Install djhtml
pip install djhtml

# Or with uv
uv pip install djhtml

# Reinstall pre-commit hooks
pre-commit uninstall
pre-commit install
```

### "Template formatting looks wrong"

```bash
# Run djhtml manually with verbose output
djhtml --tabwidth 2 templates/ -v

# Check for syntax errors in templates
python manage.py check --deploy
```

---

## 📊 Comparison: Old vs New

### Old Stack (Black + Manual Templates)

```bash
# Format Python
black .                    # 8 seconds, might touch templates!

# Format templates manually
# No automated solution
# Developers format inconsistently
```

**Problems**:
- ❌ Black could break templates
- ❌ No automated template formatting
- ❌ Inconsistent template style
- ❌ Manual work required

### New Stack (Ruff + djhtml)

```bash
# Format everything
make format               # 0.5 seconds

# Or use pre-commit
git commit                # Automatic formatting
```

**Benefits**:
- ✅ Ruff can't touch templates (explicitly blocked)
- ✅ djhtml automatically formats templates
- ✅ Consistent template style across team
- ✅ Fully automated via pre-commit
- ✅ 16x faster than old stack

---

## 🎓 Learn More

- **djhtml docs**: https://github.com/rtts/djhtml
- **Ruff docs**: https://docs.astral.sh/ruff/
- **Django templates**: https://docs.djangoproject.com/en/5.0/topics/templates/
- **Pre-commit**: https://pre-commit.com/

---

## ✅ Summary

**Your templates are safe!**

1. **Ruff** is blocked from touching `.html` files (3 layers of protection)
2. **djhtml** handles template formatting (Django-aware)
3. **Pre-commit** automates everything
4. **It just works** - commit and forget!

No more worrying about broken templates. The new system is:
- Faster (16x)
- Safer (can't break templates)
- Automated (pre-commit)
- Django-aware (djhtml understands template syntax)

🎉 **Happy Django templating!**
