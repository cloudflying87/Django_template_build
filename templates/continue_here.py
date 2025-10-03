#!/usr/bin/env python3
"""
Continue Here - Project Setup Automation
==========================================
This script automates the remaining setup steps after the initial project
structure has been created by setup_new_project.py.

Run this from your NEW project directory (not BuildTemplate).
"""

import subprocess
import sys
from pathlib import Path
import shutil


class ContinueSetup:
    """Automate the continuation of project setup."""

    def __init__(self):
        self.project_dir = Path.cwd()
        self.project_name = "{project_name}"
        self.python_version = "{python_version}"

    def print_header(self, text):
        """Print a formatted header."""
        print(f"\n{'=' * 60}")
        print(f"  {text}")
        print('=' * 60)

    def print_step(self, number, text):
        """Print a step number and description."""
        print(f"\n{'─' * 60}")
        print(f"📍 Step {number}: {text}")
        print('─' * 60)

    def run_command(self, cmd, description, check=True, shell=False, show_output=True):
        """Run a command and handle errors."""
        print(f"\n▶ {description}")
        print(f"  Command: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")

        try:
            if show_output:
                # Don't capture output - show it in real-time
                if shell:
                    result = subprocess.run(cmd, shell=True, check=check)
                else:
                    result = subprocess.run(cmd, check=check)

                if result.returncode == 0:
                    print("✅ Success")
                return True
            else:
                # Capture output (for quick commands)
                if shell:
                    result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
                else:
                    result = subprocess.run(cmd, check=check, capture_output=True, text=True)

                if result.stdout:
                    print(result.stdout)
                if result.returncode == 0:
                    print("✅ Success")
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"   {e.stderr}")
            if check:
                raise
            return False
        except FileNotFoundError:
            print(f"❌ Command not found")
            return False

    def _create_manage_py(self):
        """Create manage.py that explicitly uses development settings."""
        manage_content = '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Explicitly use development settings by default
    # Override in production with: DJANGO_SETTINGS_MODULE=config.settings.production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''
        manage_py = self.project_dir / "manage.py"
        manage_py.write_text(manage_content)
        manage_py.chmod(0o755)

    def _create_missing_config_files(self):
        """Create urls.py, wsgi.py, and asgi.py if they don't exist."""
        config_dir = self.project_dir / "config"

        # Create urls.py if missing
        if not (config_dir / "urls.py").exists():
            urls_content = '''"""
URL configuration for {project_name} project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.core.urls')),  # Homepage and core views
    path('admin/', admin.site.urls),
    path('health/', include('health_check.urls')),
]

# Add accounts URLs if the app exists
try:
    urlpatterns.append(path('accounts/', include('apps.accounts.urls')))
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Add browser auto-reload (if installed)
    try:
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    except ImportError:
        pass

    # Add debug toolbar (if installed)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
'''
            (config_dir / "urls.py").write_text(urls_content.format(project_name=self.project_name))

        # Create wsgi.py if missing
        if not (config_dir / "wsgi.py").exists():
            wsgi_content = '''"""
WSGI config for {project_name} project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
'''
            (config_dir / "wsgi.py").write_text(wsgi_content.format(project_name=self.project_name))

        # Create asgi.py if missing
        if not (config_dir / "asgi.py").exists():
            asgi_content = '''"""
ASGI config for {project_name} project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
'''
            (config_dir / "asgi.py").write_text(asgi_content.format(project_name=self.project_name))

    def _create_core_homepage(self):
        """Create homepage view, URLs, and template for core app."""
        core_dir = self.project_dir / "apps" / "core"

        # Create core URLs
        core_urls_content = '''"""
Core app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
'''
        (core_dir / "urls.py").write_text(core_urls_content)

        # Create home view
        views_content = '''"""
Core app views.
"""
from django.shortcuts import render


def home(request):
    """Homepage view."""
    context = {
        'project_name': '{project_name}',
    }
    return render(request, 'core/home.html', context)
'''
        (core_dir / "views.py").write_text(views_content.format(project_name=self.project_name))

        # Create templates directory and home template
        templates_dir = core_dir / "templates" / "core"
        templates_dir.mkdir(parents=True, exist_ok=True)

        home_template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }} - Ready!</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }}

        .container {{
            text-align: center;
            max-width: 600px;
        }}

        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: fadeInUp 0.6s ease-out;
        }}

        .emoji {{
            font-size: 5rem;
            margin-bottom: 2rem;
            animation: bounce 1s ease-in-out infinite;
        }}

        p {{
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.95;
            animation: fadeInUp 0.6s ease-out 0.2s both;
        }}

        .info {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 2rem;
            margin-top: 2rem;
            animation: fadeInUp 0.6s ease-out 0.4s both;
        }}

        .info h2 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }}

        .links {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 1.5rem;
        }}

        .links a {{
            color: white;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .links a:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-20px); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎉</div>
        <h1>You Made It!</h1>
        <p>{{ project_name }} is up and running</p>

        <div class="info">
            <h2>Now Start Programming</h2>
            <div class="links">
                <a href="/admin/">Admin Panel</a>
                <a href="/health/">Health Check</a>
            </div>
        </div>
    </div>
</body>
</html>
'''
        (templates_dir / "home.html").write_text(home_template_content)
        print("✅ Created homepage at /")

    def create_pyenv(self):
        """Create and activate Python environment."""
        self.print_step(1, "Creating Python Environment")

        # Check if pyenv is installed
        try:
            subprocess.run(['pyenv', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠️  pyenv not found. Skipping virtual environment creation.")
            print("   You can install pyenv later or use venv:")
            print(f"   python3 -m venv .venv")
            print(f"   source .venv/bin/activate")
            return False

        # Check if environment already exists
        result = subprocess.run(
            ['pyenv', 'virtualenvs', '--bare'],
            capture_output=True,
            text=True
        )

        if self.project_name in result.stdout:
            print(f"✅ Environment '{self.project_name}' already exists")
            return True

        # Create environment
        success = self.run_command(
            ['pyenv', 'virtualenv', self.python_version, self.project_name],
            f"Creating pyenv environment: {self.project_name}",
            check=False
        )

        if success:
            print(f"\n✅ Environment created!")
            print(f"   It will auto-activate when you cd into this directory")
            print(f"   (thanks to .python-version file)")

        return success

    def install_uv(self):
        """Install UV package manager."""
        self.print_step(2, "Installing UV Package Manager (Optional)")

        # Check if already installed
        try:
            subprocess.run(['uv', '--version'], capture_output=True, check=True)
            print("✅ UV already installed")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        print("UV is 10-100x faster than pip!")
        if input("Install UV? (Y/n): ").lower() != 'n':
            return self.run_command(
                [sys.executable, '-m', 'pip', 'install', 'uv'],
                "Installing UV via pip",
                check=False
            )
        else:
            print("⏭️  Skipping UV installation")
            return False

    def install_dependencies(self):
        """Install project dependencies."""
        self.print_step(3, "Installing Dependencies")

        print("\n⏱️  This may take a few minutes on first run...")

        makefile = self.project_dir / "Makefile"
        if not makefile.exists():
            print("⚠️  Makefile not found. Installing manually...")
            return self.run_command(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements/development.txt'],
                "Installing dependencies with pip",
                check=False
            )

        # Try using make commands
        self.run_command(
            ['make', 'install-uv'],
            "Installing UV via Makefile",
            check=False
        )

        return self.run_command(
            ['make', 'install'],
            "Installing all dependencies",
            check=False
        )

    def setup_django(self):
        """Set up Django project structure."""
        self.print_step(4, "Setting Up Django Project")

        # Check if already set up (look for manage.py or config/settings/)
        manage_py = self.project_dir / "manage.py"
        config_settings = self.project_dir / "config" / "settings"

        if manage_py.exists():
            print("✅ Django project already configured")
            return True

        # If config/settings/ exists but manage.py doesn't, create it manually
        if config_settings.exists():
            print("✅ Django settings found, creating Django files...")
            self._create_manage_py()
            self._create_missing_config_files()
            self._create_core_homepage()
            print("✅ Django project configured with pre-existing settings")
            return True

        print("\n📋 Django Setup Options:")
        print("1. Automatic (recommended - uses existing config/settings/)")
        print("2. Manual (you configure yourself)")
        print("3. Skip for now")

        choice = input("\nChoice (1-3): ").strip() or "1"

        if choice == "3":
            print("⏭️  Skipping Django setup")
            return False

        if choice == "2":
            print("\n📝 Manual setup instructions:")
            print("1. django-admin startproject config .")
            print("2. python manage.py startapp core")
            print("3. mv core apps/")
            print("4. Update config/settings.py with pre-configured settings")
            return False

        # Automatic setup
        try:
            # Create Django project
            self.run_command(
                ['django-admin', 'startproject', 'config', '.'],
                "Creating Django project structure",
                check=True
            )

            # Create core app
            self.run_command(
                ['python', 'manage.py', 'startapp', 'core'],
                "Creating core app",
                check=True
            )

            # Move core to apps/
            core_dir = self.project_dir / "core"
            apps_core = self.project_dir / "apps" / "core"
            if core_dir.exists() and not apps_core.exists():
                shutil.move(str(core_dir), str(apps_core))
                print("✅ Moved core app to apps/core")

            # Remove Django's default settings.py (we have pre-configured ones)
            default_settings = self.project_dir / "config" / "settings.py"
            if default_settings.exists():
                default_settings.unlink()
                print("✅ Removed default settings.py (using pre-configured settings/)")

            # Update manage.py to explicitly use development settings
            self._create_manage_py()
            print("✅ Updated manage.py to use config.settings.development")

            # Create homepage
            self._create_core_homepage()

            print("\n✅ Django project created!")
            print("   Using pre-configured settings in config/settings/")

            return True

        except Exception as e:
            print(f"❌ Django setup failed: {e}")
            print("   Please set up Django manually - see NEXT_STEPS.md")
            return False

    def run_initial_setup(self):
        """Run initial Django setup commands."""
        self.print_step(5, "Running Initial Setup")

        makefile = self.project_dir / "Makefile"
        if makefile.exists():
            return self.run_command(
                ['make', 'setup'],
                "Running make setup (migrations, pre-commit hooks, etc.)",
                check=False
            )
        else:
            # Manual setup
            print("Running migrations...")
            self.run_command(
                ['python', 'manage.py', 'migrate'],
                "Applying database migrations",
                check=False
            )
            return True

    def initialize_git(self):
        """Initialize git repository and create initial commit."""
        self.print_step(6, "Initializing Git Repository")

        git_dir = self.project_dir / ".git"

        if git_dir.exists():
            print("✅ Git repository already initialized")
        else:
            self.run_command(
                ['git', 'init'],
                "Initializing git repository",
                check=True
            )

        # Check if there are uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            if input("\nCreate initial commit? (Y/n): ").lower() != 'n':
                self.run_command(
                    ['git', 'add', '.'],
                    "Staging all files",
                    check=False
                )

                self.run_command(
                    ['git', 'commit', '-m', 'Initial project setup'],
                    "Creating initial commit",
                    check=False
                )

                print("\n📝 Next: Add remote and push")
                print(f"   git remote add origin git@github.com:username/{self.project_name}.git")
                print(f"   git push -u origin main")
        else:
            print("✅ No changes to commit")

        return True

    def show_next_steps(self):
        """Show what to do next."""
        self.print_header("✅ Setup Complete!")

        print(f"""
🎉 Your {self.project_name} project is ready!

🚀 Start Development:
   make run
   # or
   python manage.py runserver

📝 Create Superuser:
   python manage.py createsuperuser

🌐 Access Your Site:
   - Homepage: http://localhost:8000 (You made it! 🎉)
   - Admin: http://localhost:8000/admin
   - Health: http://localhost:8000/health

📚 Documentation:
   - Quick reference: NEXT_STEPS.md
   - Complete guides: docs/SETUP_GUIDE.md
   - Beginner tutorial: docs/BEGINNERS_GUIDE.md
   - Your design system: docs/STYLE_GUIDE.md

🧹 Clean Up:
   Once you're up and running, you can delete:
   - continue_here.py (this script)
   - NEXT_STEPS.md (the guide)

Happy coding! 🎉
""")

    def run(self):
        """Run the complete continuation setup."""
        self.print_header(f"🚀 Continue Setup: {self.project_name}")

        print(f"""
This script will help you complete your project setup.

📍 Current directory: {self.project_dir}
🐍 Python version: {self.python_version}

We'll automate:
  1. Creating Python environment
  2. Installing dependencies
  3. Setting up Django
  4. Running migrations
  5. Initializing git

Press Ctrl+C at any time to stop.
""")

        if input("Continue? (Y/n): ").lower() == 'n':
            print("\n❌ Setup cancelled")
            print("   You can run this script again anytime")
            print("   Or follow manual steps in NEXT_STEPS.md")
            return

        try:
            # Run each step
            self.create_pyenv()
            self.install_uv()
            self.install_dependencies()
            self.setup_django()
            self.run_initial_setup()
            self.initialize_git()

            # Show what's next
            self.show_next_steps()

        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted")
            print("   You can run this script again to continue")
            print("   Or follow manual steps in NEXT_STEPS.md")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Error during setup: {e}")
            print("   See NEXT_STEPS.md for manual setup instructions")
            sys.exit(1)


def main():
    """Main entry point."""
    setup = ContinueSetup()
    setup.run()


if __name__ == "__main__":
    main()
