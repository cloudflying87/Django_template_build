# {project_name_upper} - Project Setup Summary

**Generated on**: {generated_date}

## 🎯 Project Overview

**Name**: {project_name}
**Description**: {project_description}
**Domain**: {domain}
**Target Users**: {target_users}
**Python Version**: {python_version}

## 🎨 Design & Theme

**Primary Color**: {primary_color}
**Secondary Color**: {secondary_color}
**Accent Color**: {accent_color}
**Design Style**: {design_style}
**Border Radius**: {border_radius}
**Shadow Style**: {shadow_style}
**Dark Mode**: {dark_mode}
**Mobile Navigation**: {mobile_nav}
**Share Image**: {share_image}

## ⚙️ Technical Configuration

**Development Database**: {dev_database}
**Features Enabled**:
{features_list}

**Remote Backup**: {remote_backup}
{remote_server_info}

## 🏗️ Architecture Details

**Development Workflow**:
- Local development with pyenv (no Docker)
- Hot reload with `python manage.py runserver`
- {dev_database} database for development

**Production Stack**:
- Docker Compose orchestration
- PostgreSQL database
- Nginx web server with security headers
- Gunicorn WSGI server
- Automated build/deploy via build.sh

**CSS Architecture**:
- Custom component system (NO Bootstrap/Tailwind)
- Mobile-first responsive design
- CSS variables for consistent theming
- Component-based organization in static/css/components/

## 📁 Generated Project Structure

```
{project_name}/
├── CLAUDE.md                    # Project memory (IMPORTANT for AI context)
├── build.sh                     # Production deployment automation
├── Makefile                     # Development commands (make help)
├── .python-version              # Auto pyenv activation
├── .pre-commit-config.yaml      # Code quality automation
├── README.md                    # Project overview
│
├── apps/                        # Django applications
│   └── core/                   # Base functionality
├── config/                      # Django settings
│   └── settings/               # Environment-specific settings
├── static/                      # Static assets
│   ├── css/                    # Custom CSS framework
│   │   ├── base.css            # Generated theme with your colors
│   │   └── components/         # Reusable components (buttons, forms, etc.)
│   ├── img/                    # Images
│   │   └── default-share.*     # Default share image (PWA/OG)
│   ├── js/                     # JavaScript
│   │   └── service-worker.js   # PWA service worker
│   └── manifest.json           # PWA manifest
├── templates/                   # Django templates
├── docs/                       # Comprehensive documentation
│   ├── SETUP_GUIDE.md         # Complete setup instructions
│   ├── BEGINNERS_GUIDE.md     # Tutorial for new developers
│   ├── STYLE_GUIDE.md         # Custom styling guidelines
│   ├── CODING_GUIDE.md        # Development standards
│   ├── FILE_HANDLING.md       # File upload & storage guide
│   └── PWA_SETUP.md           # PWA & Open Graph configuration
│
├── requirements/               # Python dependencies
├── nginx/                      # Production nginx config
├── docker-compose.yml          # Production containers
└── Dockerfile                  # Production image
```

## 🚀 Key Commands Reference

**Development**:
```bash
make run          # Start development server
make test         # Run tests
make shell        # Django shell
make migrate      # Database migrations
make format       # Auto-format code
make lint         # Check code quality
```

**Production**:
```bash
make deploy       # Deploy with backup
make backup       # Backup database
./build.sh -r -d $(date +%Y%m%d)  # Full rebuild
```

## 🎯 Domain-Specific Context

**Industry**: {domain}
**Compliance Requirements**: {compliance_reqs}
**Special Features**: {special_features}

## 📋 Next Development Tasks

1. **Django Setup**:
   - Move settings.py to config/settings/ structure
   - Create base, development, and production settings
   - Add 'apps.core' to INSTALLED_APPS

2. **Model Development**:
   - Define domain models in apps/core/models.py
   - Create migrations and migrate
   - Set up admin interface

3. **Frontend**:
   - Custom CSS components are ready in static/css/
   - Mobile-first templates in templates/
   - No Bootstrap/Tailwind - use custom system

4. **Quality Setup**:
   - Pre-commit hooks configured
   - Code formatting with black/isort
   - Linting with flake8

## 🤖 AI Assistant Instructions

When helping with this project:

1. **NEVER suggest Bootstrap/Tailwind** - We have a complete custom CSS system
2. **Always think mobile-first** - Every component starts with mobile design
3. **Use the custom CSS variables** - Primary: {primary_color}, etc.
4. **Follow the build.sh pattern** - Production deployment via Docker
5. **Reference CLAUDE.md** - Contains living project context
6. **Domain focus**: This is a {domain} application for {target_users}

## 🔧 Quick Context for Development

**Current Status**: Fresh project setup completed
**Ready for**: Django project creation and initial model development
**Architecture**: Same proven patterns as Keep-Logging project
**Styling**: Custom {design_style} theme with {primary_color} primary color
**Deployment**: Docker production, pyenv development

---

*This summary provides complete context for AI assistants and developers joining the project.*
