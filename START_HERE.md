# 🚀 START HERE - Django Project Template Factory

Welcome! This is a **template factory** that generates complete Django projects with the same proven architecture as Keep-Logging.

## 🏭 How It Works

This template stays **permanently** in one location and creates new projects as siblings:

```
/Users/yourname/Coding/
├── BuildTemplate/          ← This stays here forever
│   ├── setup_new_project.py
│   └── (all template files)
├── my-first-project/       ← Created by the wizard
├── my-second-project/      ← Created by the wizard
└── my-third-project/       ← Created by the wizard
```

**Key concept**: The wizard creates your new project in the **parent directory** so BuildTemplate remains untouched for future use.

## 📋 Quick Start

### Step 1: Run the Wizard (2 minutes)

```bash
cd /path/to/BuildTemplate
python setup_new_project.py
```

Answer the questions about:
- Project name, colors, design style
- Features you need (API, Celery, Redis, etc.)
- Industry compliance requirements

The wizard creates your project in the parent directory and offers to open it in VSCode.

### Step 2: Initial Django Setup (5 minutes)

After the wizard completes, navigate to your new project:

```bash
cd ../your-project-name
```

**Create virtual environment:**
```bash
pyenv virtualenv 3.13.3 your-project-name
cd .  # Re-enter directory to activate (thanks to .python-version file)
```

**Install dependencies:**
```bash
make install    # Uses UV if available (10-100x faster than pip)
```

**Create Django project:**
```bash
django-admin startproject config .
python manage.py startapp core
mv core apps/
```

**⚠️ IMPORTANT: Configure URLs**

Open the generated `CONFIGURE_URLS.md` file and follow instructions to add:
- Health check endpoints (`/health/`)
- Browser auto-reload (`/__reload__/`)
- Debug toolbar (`/__debug__/`)

**Run initial setup:**
```bash
make setup      # Runs migrations, creates superuser, installs pre-commit hooks
```

**Start development:**
```bash
make run        # Django development server with auto-reload!
```

Visit http://localhost:8000/health/ to verify health checks are working.

### Step 3: Start Building (ongoing)

Your project is now ready with:
- ✅ Structured logging (structlog)
- ✅ Health check endpoints
- ✅ Browser auto-reload
- ✅ Modern code quality tools (ruff, mypy, bandit)
- ✅ Custom CSS framework (your colors!)
- ✅ Production-ready Docker setup

**Key files to read:**
- `CONFIGURE_URLS.md` - URL setup instructions (do this first!)
- `PROJECT_SETUP_SUMMARY.md` - Your project configuration
- `CLAUDE.md` - AI assistant context (logging patterns, best practices)
- `docs/SETUP_GUIDE.md` - Complete setup documentation

## 🎯 What You'll Get

### ✅ Complete Project Structure
- Django apps in `apps/` directory
- Production-ready Docker setup
- Custom CSS framework (no Bootstrap!)
- Nginx configuration
- Database setup (PostgreSQL + Redis)

### ✅ Optional Features (you choose during setup)
- **Cloudflare Tunnel**: Secure public access
- **Celery**: Background task processing
- **REST API**: DRF integration
- **Sentry**: Error tracking
- **Custom theming**: Your brand colors

### ✅ Modern Development Tools
- **structlog**: Structured logging with JSON output
- **django-health-check**: Health endpoints for monitoring
- **django-browser-reload**: Auto-refresh on code changes
- **django-migration-linter**: Catch unsafe migrations
- **ruff**: Ultra-fast linting & formatting (10-100x faster)
- **mypy**: Type checking for Python
- **UV**: Blazing-fast package installation

### ✅ Documentation & Tools
- **CLAUDE.md**: AI assistant context with logging best practices
- **CONFIGURE_URLS.md**: URL setup instructions
- **Style guides**: Complete CSS/coding standards
- **Build scripts**: One-command deployment
- **Pre-commit hooks**: Automated code quality checks

## 🔧 Commands Reference

```bash
# Initial setup (run from BuildTemplate directory)
python setup_new_project.py           # Run setup wizard to create new project

# Development (run from your NEW project directory)
make run          # Start development server
make test         # Run tests
make shell        # Django shell
make migrate      # Run migrations

# Production (run from your NEW project directory)
make deploy       # Deploy with backup
./build.sh -r -d  # Full rebuild and deploy
```

## 🎨 What Makes This Special

### Same Architecture as Keep-Logging
- ✅ Proven directory structure
- ✅ Custom CSS component system
- ✅ Custom Colors
- ✅ PWA-ready offline functionality
- ✅ Security-hardened Docker setup

### Industry-Specific Features
The wizard asks about your industry and adds appropriate:
- Compliance requirements (HIPAA, SOX, FAR, etc.)
- Special features for your domain
- Regulatory context in documentation

### Smart Configuration
- Only includes services you actually need
- Removes unused Docker services
- Configures environment variables automatically
- Sets up proper .gitignore for security

## 📚 After Setup

Once setup completes, you'll have:

1. **PROJECT_SETUP_SUMMARY.md**: Complete record of your choices in your new project
2. **Ready-to-code Django project**: Just add your models and views
3. **Production deployment**: `make deploy` handles everything
4. **AI-ready documentation**: CLAUDE.md has full context

## 🏭 Create More Projects

Want to create another project? Just run the wizard again:

```bash
cd /path/to/BuildTemplate
python setup_new_project.py
```

Each project will be created as a new sibling directory. The BuildTemplate folder stays intact!

## 🆘 Need Help?

- **Setup issues**: Check the generated `docs/SETUP_GUIDE.md`
- **Styling questions**: See `docs/STYLE_GUIDE.md`
- **Deployment problems**: Review `build.sh` script
- **General development**: Reference `CLAUDE.md` for AI assistance

---

**🎉 Ready to build something amazing?**

Run `python setup_new_project.py` and let's get started!