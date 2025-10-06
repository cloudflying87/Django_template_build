#!/usr/bin/env python3
"""
Interactive Django Project Setup Script
Asks questions and automatically fills in all template documents
"""

import os
import sys
import re
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ProjectSetup:
    def __init__(self):
        self.answers = {}
        self.project_dir = None  # Will be set after getting project name
        self.resuming = False  # Track if we're resuming from previous run

        # Create temp directory for wizard files
        self.temp_dir = Path.cwd() / ".wizard_temp"
        self.temp_dir.mkdir(exist_ok=True)

        # Create README in temp directory to explain its purpose
        readme_path = self.temp_dir / "README.txt"
        if not readme_path.exists():
            readme_path.write_text("""
This directory contains temporary files created by the Django project setup wizard.

What's stored here:
- Progress files (progress_*.json) - Your answers saved during wizard runs
- These files allow you to resume setup if something fails

This directory is automatically cleaned up when setup completes successfully.

If you see old files here, you can safely delete this entire directory.
It's excluded from git via .gitignore.
""".strip())

        # Save progress in temp directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_file = self.temp_dir / f"progress_{timestamp}.json"

        # Try to load previous answers if they exist
        self.load_progress()

    def run(self):
        """Run the complete setup process."""
        # Only show header and ask questions if not resuming
        if not self.resuming:
            print("🚀 Django Project Setup Wizard")
            print("=" * 50)
            print("This wizard will help you set up a new Django project")
            print("with custom styling, build scripts, and documentation.\n")

            # Ask setup mode
            setup_mode = self.ask_setup_mode()

            if setup_mode == 'quick':
                self.run_quick_setup()
            else:
                self.run_advanced_setup()

            # Show summary
            self.show_summary()
        else:
            # Resuming - show brief summary
            print("\n" + "=" * 50)
            print("📊 Resuming Setup")
            print("=" * 50)
            print(f"\nProject: {self.answers.get('project_name', 'Unknown')}")
            print(f"Description: {self.answers.get('project_description', 'N/A')}")
            print(f"Domain: {self.answers.get('domain', 'N/A')}")

        # Confirm and create
        if self.confirm_setup():
            try:
                self.create_project_structure()
                self.generate_env_file()  # Generate .env with secrets
                self.fill_templates()
                self.generate_css()
                self.create_django_project()

                # Generate auth system if requested (default: yes in quick, optional in advanced)
                if self.answers.get('include_auth', True):
                    self.generate_auth_system()

                self.generate_summary_file()
                self.generate_continue_files()  # Generate continuation script and guide
                self.show_next_steps()
                self.offer_open_vscode()

                # Clean up temp directory on successful completion
                self.cleanup_temp_files()
                print("\n✨ Wizard temp files cleaned up")

            except Exception as e:
                print(f"\n❌ Error during setup: {e}")
                print(f"\n💾 Your answers have been saved to: {self.save_file}")
                print("   You can run the script again to resume from where you left off.")
                raise  # Re-raise to show full traceback
        else:
            print("\n❌ Setup cancelled.")

    def save_progress(self):
        """Save current answers to recover from crashes."""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.answers, f, indent=2)
        except Exception as e:
            # Don't fail the whole script if we can't save
            print(f"  ⚠️  Warning: Could not save progress: {e}")

    def load_progress(self):
        """Load previous answers if available."""
        # Check for any progress files in temp directory
        if self.temp_dir.exists():
            progress_files = sorted(self.temp_dir.glob("progress_*.json"), reverse=True)

            if progress_files:
                # Use most recent progress file
                latest_progress = progress_files[0]

                try:
                    with open(latest_progress, 'r') as f:
                        saved_answers = json.load(f)

                    print("\n💾 Found previous setup in progress!")
                    print(f"   Project: {saved_answers.get('project_name', 'Unknown')}")
                    print(f"   Saved: {latest_progress.name}")

                    resume = input("\n   Resume previous setup? (Y/n): ").lower()
                    if resume != 'n':
                        self.answers = saved_answers
                        if 'project_name' in self.answers:
                            self.project_dir = Path.cwd().parent / self.answers['project_name']
                        self.save_file = latest_progress  # Use existing file
                        self.resuming = True  # Mark as resuming
                        print("   ✓ Resumed previous setup")
                        print("   ⏩ Skipping questions, going directly to project creation...")
                    else:
                        # Start fresh - clean up old progress files
                        self.cleanup_temp_files()
                        print("   ✓ Starting fresh setup")

                except Exception as e:
                    print(f"  ⚠️  Warning: Could not load previous progress: {e}")
                    print("   Starting fresh setup")

    def cleanup_temp_files(self):
        """Clean up temporary wizard files."""
        try:
            if self.temp_dir.exists():
                # Remove all progress files
                for file in self.temp_dir.glob("progress_*.json"):
                    file.unlink()

                # Check if only README remains
                remaining_files = list(self.temp_dir.glob("*"))
                if len(remaining_files) <= 1 and all(f.name == "README.txt" for f in remaining_files):
                    # Clean up everything including README
                    for file in remaining_files:
                        file.unlink()
                    self.temp_dir.rmdir()

        except Exception as e:
            print(f"  ⚠️  Warning: Could not clean up temp files: {e}")

    def ask_setup_mode(self) -> str:
        """Ask user for setup mode."""
        print("\n📋 Setup Mode")
        print("-" * 30)
        print("\n1. Quick Start (recommended)")
        print("   ✓ Smart defaults for rapid development")
        print("   ✓ Minimal questions (5 minutes)")
        print("   ✓ Modern best practices")
        print("\n2. Advanced Setup")
        print("   ✓ Full customization")
        print("   ✓ All options available")
        print("   ✓ Complete control")

        choice = self.get_numeric_choice(2)
        return 'quick' if choice == 1 else 'advanced'

    def run_quick_setup(self):
        """Run quick setup with smart defaults."""
        print("\n⚡ Quick Setup Mode")
        print("=" * 50)

        # Essential info only
        self.collect_project_info()

        # Smart defaults for auth (always include in quick mode)
        self.answers['include_auth'] = True
        self.answers['auth_type'] = 'hybrid'  # Web + API

        # Simple choice: Email or Username login?
        print("\n🔐 User Login Method")
        print("-" * 30)
        print("1. Email address (modern, recommended)")
        print("2. Username (traditional)")
        choice = self.get_numeric_choice(2)
        self.answers['login_method'] = 'email' if choice == 1 else 'username'

        # Auto-enable 2FA for sensitive domains
        self.answers['enable_2fa'] = self._is_sensitive_domain()
        if self.answers['enable_2fa']:
            print("✓ Two-factor authentication enabled (recommended for your domain)")

        # Security defaults
        self.answers['email_verification'] = True
        self.answers['password_strength'] = True

        # Quick style choices (just colors)
        print("\n🎨 Brand Colors")
        print("-" * 30)
        self.answers['primary_color'] = self.get_hex_color("Primary color", "0066cc")
        self.answers['secondary_color'] = self.get_hex_color("Secondary color", "6c757d")
        self.answers['accent_color'] = self.get_hex_color("Accent color", "28a745")

        # Smart style defaults
        self.answers['design_style'] = 'modern'
        self.answers['border_radius'] = '8px'
        self.answers['shadow_style'] = 'medium'
        self.answers['dark_mode'] = True
        self.answers['mobile_nav'] = 'hamburger'

        # Optional: Share image
        self._quick_share_image_prompt()

        # Technical defaults (optimized for quick start)
        self.answers['python_version'] = '3.13.1'
        self.answers['dev_database'] = 'sqlite'  # SQLite for simplicity
        self.answers['use_celery'] = False
        self.answers['use_redis'] = False  # Keep it simple for quick start
        self.answers['use_api'] = True  # Hybrid includes API
        self.answers['use_sentry'] = False
        self.answers['use_cloudflare'] = False
        self.answers['remote_server'] = None
        self.answers['remote_backup_dir'] = None

        # Domain specifics
        self.answers['compliance_reqs'] = self._get_default_compliance()
        self.answers['special_features'] = ''

        # Save progress
        self.save_progress()

        print("\n✓ Quick setup complete with smart defaults!")

    def run_advanced_setup(self):
        """Run full advanced setup with all options."""
        print("\n⚙️  Advanced Setup Mode")
        print("=" * 50)

        # Collect basic project info first (needed for domain-based defaults)
        self.collect_project_info()

        # Ask about authentication first
        print("\n👤 Authentication System")
        print("-" * 30)
        include_auth = input("Include authentication system (custom User model + login/register)? (Y/n): ").lower()
        self.answers['include_auth'] = include_auth != 'n'

        if not self.answers['include_auth']:
            print("  ⚠️  Skipping authentication - project will use Django's default User model")
            print("  💡 Note: You can't add a custom User model later without database migration pain!")
            # Set defaults for skipped auth
            self.answers['auth_type'] = None
            self.answers['login_method'] = None
            self.answers['enable_2fa'] = False
            self.answers['email_verification'] = False
            self.answers['password_strength'] = True  # Still use Django's defaults
        else:
            # Collect auth configuration
            self.collect_authentication_setup()

        # Collect all other answers (existing flow)
        self.collect_style_preferences()
        self.collect_technical_choices()
        self.collect_domain_specific()

        # Save progress after all answers collected
        self.save_progress()

    def _quick_share_image_prompt(self):
        """Quick prompt for share image."""
        if input("\nAdd a share image for social media? (y/N): ").lower() == 'y':
            while True:
                image_path = input("Path to image file: ").strip()
                image_path = Path(image_path).expanduser()
                if image_path.exists() and image_path.is_file():
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                        self.answers['share_image_path'] = image_path
                        break
                    else:
                        print("  ❌ Please provide a valid image file")
                else:
                    print("  ❌ File not found")
        else:
            self.answers['share_image_path'] = None

    def _is_sensitive_domain(self) -> bool:
        """Check if domain requires extra security."""
        sensitive = ['health', 'medical', 'finance', 'banking', 'aviation', 'government']
        return any(term in self.answers['domain'].lower() for term in sensitive)

    def _get_default_compliance(self) -> str:
        """Get default compliance requirements based on domain."""
        domain = self.answers['domain'].lower()
        if 'health' in domain or 'medical' in domain:
            return 'HIPAA compliance, patient data protection'
        elif 'finance' in domain or 'banking' in domain:
            return 'SOX compliance, financial regulations'
        elif 'aviation' in domain:
            return 'FAA compliance, safety regulations'
        else:
            return 'Standard security practices'
    
    def collect_project_info(self):
        """Collect basic project information."""
        print("\n📋 Basic Project Information")
        print("-" * 30)
        
        # Project name
        while True:
            project_name = input("Project name (e.g., 'my-awesome-app'): ").strip()
            if re.match(r'^[a-z0-9-]+$', project_name):
                self.answers['project_name'] = project_name
                self.answers['project_name_snake'] = project_name.replace('-', '_')
                # Set project directory based on project name (in parent directory)
                self.project_dir = Path.cwd().parent / project_name
                break
            else:
                print("❌ Project name should only contain lowercase letters, numbers, and hyphens")
        
        # Project description
        self.answers['project_description'] = input("Brief project description: ").strip()
        
        # Industry/Domain
        print("\nIndustry/Domain:")
        domains = [
            "Aviation/Aerospace",
            "Healthcare/Medical", 
            "Finance/Banking",
            "E-commerce/Retail",
            "Education",
            "Government",
            "Technology/SaaS",
            "Other"
        ]
        for i, domain in enumerate(domains, 1):
            print(f"  {i}. {domain}")
        
        choice = self.get_numeric_choice(len(domains))
        self.answers['domain'] = domains[choice - 1]
        
        if self.answers['domain'] == "Other":
            self.answers['domain'] = input("Please specify: ").strip()
        
        # Target users
        self.answers['target_users'] = input("Target users (e.g., 'pilots', 'doctors', 'customers'): ").strip()
        
        # Remote server setup (optional)
        if input("\nDo you have a remote backup server? (y/N): ").lower() == 'y':
            self.answers['remote_server'] = input("Remote server (user@host): ").strip()
            self.answers['remote_backup_dir'] = input("Remote backup directory: ").strip()
        else:
            self.answers['remote_server'] = None
            self.answers['remote_backup_dir'] = None
    
    def collect_style_preferences(self):
        """Collect style and theme preferences."""
        print("\n🎨 Style & Theme Preferences")
        print("-" * 30)
        
        # Brand colors
        print("\nBrand Colors (enter hex codes without #):")
        self.answers['primary_color'] = self.get_hex_color("Primary color", "0066cc")
        self.answers['secondary_color'] = self.get_hex_color("Secondary color", "6c757d")
        self.answers['accent_color'] = self.get_hex_color("Accent color", "28a745")
        
        # Design style
        print("\nOverall Design Style:")
        styles = [
            ("professional", "Professional & Corporate (clean, trustworthy)"),
            ("modern", "Modern & Minimal (lots of white space)"),
            ("friendly", "Friendly & Approachable (rounded corners, warm)"),
            ("technical", "Technical & Precise (sharp lines, data-focused)"),
            ("creative", "Creative & Bold (unique elements)")
        ]
        for i, (key, desc) in enumerate(styles, 1):
            print(f"  {i}. {desc}")
        
        choice = self.get_numeric_choice(len(styles))
        self.answers['design_style'] = styles[choice - 1][0]
        
        # Border radius
        print("\nBorder Radius Preference:")
        radii = [
            ("0px", "Sharp corners (technical feel)"),
            ("4px", "Subtle rounding (professional)"),
            ("8px", "Medium rounding (modern)"),
            ("16px", "High rounding (friendly)")
        ]
        for i, (value, desc) in enumerate(radii, 1):
            print(f"  {i}. {desc}")
        
        choice = self.get_numeric_choice(len(radii))
        self.answers['border_radius'] = radii[choice - 1][0]
        
        # Shadow style
        print("\nShadow Style:")
        shadows = [
            ("none", "No shadows (flat design)"),
            ("subtle", "Subtle shadows (barely visible)"),
            ("medium", "Medium shadows (clear depth)"),
            ("strong", "Strong shadows (pronounced)")
        ]
        for i, (key, desc) in enumerate(shadows, 1):
            print(f"  {i}. {desc}")
        
        choice = self.get_numeric_choice(len(shadows))
        self.answers['shadow_style'] = shadows[choice - 1][0]
        
        # Dark mode
        dark_mode = input("\nEnable dark mode support? (Y/n): ").lower()
        self.answers['dark_mode'] = dark_mode != 'n'
        
        # Mobile navigation
        print("\nMobile Navigation Style:")
        nav_styles = [
            ("bottom-tabs", "Bottom tabs (mobile-native)"),
            ("hamburger", "Hamburger menu (space-efficient)"),
            ("drawer", "Drawer/sidebar (slide-out)")
        ]
        for i, (key, desc) in enumerate(nav_styles, 1):
            print(f"  {i}. {desc}")

        choice = self.get_numeric_choice(len(nav_styles))
        self.answers['mobile_nav'] = nav_styles[choice - 1][0]

        # Default share/OG image
        print("\nDefault Share Image (for PWA & Open Graph):")
        print("  Recommended: 1200x630px PNG or JPG")
        print("  Used for social media shares and PWA icon")
        if input("Do you have an image to upload? (y/N): ").lower() == 'y':
            while True:
                image_path = input("Path to image file: ").strip()
                image_path = Path(image_path).expanduser()
                if image_path.exists() and image_path.is_file():
                    # Validate it's an image
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                        self.answers['share_image_path'] = image_path
                        break
                    else:
                        print("  ❌ Please provide a valid image file (.jpg, .png, or .webp)")
                else:
                    print("  ❌ File not found. Please enter a valid path.")
        else:
            self.answers['share_image_path'] = None
            print("  💡 Note: You can add a default share image later to static/img/default-share.jpg")
    
    def collect_technical_choices(self):
        """Collect technical preferences."""
        print("\n⚙️  Technical Choices")
        print("-" * 30)
        
        # Python version
        default_python = "3.13.1"
        python_version = input(f"Python version [{default_python}]: ").strip()
        self.answers['python_version'] = python_version or default_python
        
        # Database in development
        print("\nDevelopment Database:")
        db_choices = [
            ("sqlite", "SQLite (simple, file-based)"),
            ("postgresql", "PostgreSQL (same as production)")
        ]
        for i, (key, desc) in enumerate(db_choices, 1):
            print(f"  {i}. {desc}")
        
        choice = self.get_numeric_choice(len(db_choices))
        self.answers['dev_database'] = db_choices[choice - 1][0]
        
        # Additional features
        print("\nAdditional Features (y/N):")
        self.answers['use_celery'] = input("  Use Celery for background tasks? ").lower() == 'y'
        self.answers['use_redis'] = input("  Use Redis for caching? ").lower() == 'y'
        self.answers['use_api'] = input("  Include REST API? ").lower() == 'y'
        self.answers['use_sentry'] = input("  Include Sentry error tracking? ").lower() == 'y'
        
        # Cloudflare configuration
        print("\nCloudflare Tunnel Setup (y/N):")
        self.answers['use_cloudflare'] = input("  Set up Cloudflare Tunnel for secure public access? ").lower() == 'y'
        
        if self.answers['use_cloudflare']:
            self.answers['domain_name'] = input("  Your domain name (e.g., myapp.com): ").strip()
            print("  Note: You'll need to:")
            print("    1. Create a Cloudflare Tunnel in the dashboard")
            print("    2. Add the tunnel token to your .env file")
            print("    3. Configure DNS records in Cloudflare")

    def collect_authentication_setup(self):
        """Collect authentication configuration (for advanced mode)."""
        print("\n🔐 Authentication Setup")
        print("-" * 30)

        # Authentication type (always hybrid now, but keep for advanced mode)
        print("\nHow will users access this app?")
        auth_types = [
            ("web", "Web browser only (traditional)"),
            ("api", "API/Mobile app only"),
            ("hybrid", "Both web and API (recommended)")
        ]
        for i, (key, desc) in enumerate(auth_types, 1):
            print(f"  {i}. {desc}")

        choice = self.get_numeric_choice(len(auth_types))
        self.answers['auth_type'] = auth_types[choice - 1][0]

        # Login method
        print("\nWhat should users login with?")
        login_methods = [
            ("email", "Email address (modern, recommended)"),
            ("username", "Username (traditional)"),
            ("both", "Email or Username (most flexible)")
        ]
        for i, (key, desc) in enumerate(login_methods, 1):
            print(f"  {i}. {desc}")

        choice = self.get_numeric_choice(len(login_methods))
        self.answers['login_method'] = login_methods[choice - 1][0]

        # 2FA - auto-suggest for sensitive domains
        auto_suggest_2fa = self._is_sensitive_domain()
        default_2fa = 'Y' if auto_suggest_2fa else 'n'
        suggestion = " (RECOMMENDED for security)" if auto_suggest_2fa else ""

        enable_2fa = input(f"\nEnable Two-Factor Authentication (2FA)?{suggestion} (Y/n) [{default_2fa}]: ").lower()
        self.answers['enable_2fa'] = enable_2fa != 'n' if auto_suggest_2fa else enable_2fa == 'y'

        # Email verification
        self.answers['email_verification'] = input("Require email verification for new users? (Y/n): ").lower() != 'n'

        # Password strength
        self.answers['password_strength'] = input("Enforce strong password requirements? (Y/n): ").lower() != 'n'

    def collect_domain_specific(self):
        """Collect domain-specific requirements."""
        print(f"\n🏢 {self.answers['domain']} Specific Configuration")
        print("-" * 30)
        
        # Domain-specific questions based on industry
        if "aviation" in self.answers['domain'].lower():
            self.answers['compliance_reqs'] = "FAR compliance, flight time limits, currency tracking"
            self.answers['special_features'] = input("Special aviation features needed (e.g., 'flight logging, crew scheduling'): ").strip()
        elif "healthcare" in self.answers['domain'].lower():
            self.answers['compliance_reqs'] = "HIPAA compliance, patient data protection"
            self.answers['special_features'] = input("Special healthcare features needed (e.g., 'patient records, appointments'): ").strip()
        elif "finance" in self.answers['domain'].lower():
            self.answers['compliance_reqs'] = "SOX compliance, financial regulations"
            self.answers['special_features'] = input("Special financial features needed (e.g., 'transactions, reporting'): ").strip()
        elif "commerce" in self.answers['domain'].lower():
            self.answers['compliance_reqs'] = "PCI compliance for payments"
            self.answers['special_features'] = input("Special e-commerce features needed (e.g., 'inventory, orders'): ").strip()
        else:
            self.answers['compliance_reqs'] = input("Compliance requirements (if any): ").strip() or "None specific"
            self.answers['special_features'] = input("Special features needed: ").strip()
    
    def get_hex_color(self, prompt: str, default: str) -> str:
        """Get and validate hex color input."""
        while True:
            color = input(f"  {prompt} [{default}]: ").strip()
            color = color or default
            color = color.lstrip('#')
            
            if re.match(r'^[0-9a-fA-F]{6}$', color):
                return f"#{color.lower()}"
            else:
                print("    ❌ Please enter a valid 6-digit hex code")
    
    def get_numeric_choice(self, max_choice: int) -> int:
        """Get a numeric choice within range."""
        while True:
            try:
                choice = int(input("Choice: "))
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    print(f"Please enter a number between 1 and {max_choice}")
            except ValueError:
                print("Please enter a valid number")
    
    def show_summary(self):
        """Show configuration summary."""
        print("\n" + "=" * 50)
        print("📊 Configuration Summary")
        print("=" * 50)
        
        print(f"\nProject: {self.answers['project_name']}")
        print(f"Description: {self.answers['project_description']}")
        print(f"Domain: {self.answers['domain']}")
        print(f"Target Users: {self.answers['target_users']}")
        
        print(f"\nColors:")
        print(f"  Primary: {self.answers['primary_color']}")
        print(f"  Secondary: {self.answers['secondary_color']}")
        print(f"  Accent: {self.answers['accent_color']}")
        
        print(f"\nStyle:")
        print(f"  Design: {self.answers['design_style']}")
        print(f"  Border Radius: {self.answers['border_radius']}")
        print(f"  Shadows: {self.answers['shadow_style']}")
        print(f"  Dark Mode: {'Yes' if self.answers['dark_mode'] else 'No'}")
        if self.answers.get('share_image_path'):
            print(f"  Share Image: ✓ Provided")
        
        print(f"\nTechnical:")
        print(f"  Python Version: {self.answers['python_version']}")
        print(f"  Dev Database: {self.answers['dev_database']}")
        
        if self.answers['use_celery']:
            print(f"  ✓ Celery for background tasks")
        if self.answers['use_redis']:
            print(f"  ✓ Redis for caching")
        if self.answers['use_api']:
            print(f"  ✓ REST API")
        if self.answers['use_sentry']:
            print(f"  ✓ Sentry error tracking")
    
    def confirm_setup(self) -> bool:
        """Confirm the setup configuration."""
        print("\n" + "=" * 50)
        if self.resuming:
            return input("Continue creating project? (Y/n): ").lower() != 'n'
        else:
            return input("Proceed with setup? (Y/n): ").lower() != 'n'
    
    def create_project_structure(self):
        """Create the project directory structure."""
        print("\n📁 Creating project structure...")
        
        directories = [
            "apps/core/templates/core/includes",
            "apps/core/management/commands",
            "apps/core/migrations",
            "apps/core/static/css",
            "apps/core/static/js",
            "config/settings",
            "docs",
            "scripts",
            "static/css/components",
            "static/css/apps",
            "static/js/components",
            "static/img",
            "static/fonts",
            "templates",
            "media",
            "tests/unit",
            "tests/integration",
            "tests/factories",
            "requirements",
            "nginx",
            "backups",
        ]
        
        for directory in directories:
            (self.project_dir / directory).mkdir(parents=True, exist_ok=True)
            
            # Add __init__.py for Python packages
            if directory.startswith(('apps/', 'config/', 'tests/')):
                init_file = self.project_dir / directory / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
        
        print("✅ Directory structure created")
    
    def fill_templates(self):
        """Fill in all template files with answers."""
        print("\n📝 Generating project files...")
        
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Copy and fill build.sh
        self._process_template(
            script_dir / "build_template.sh",
            self.project_dir / "build.sh",
            {
                "your-project-name": self.answers['project_name'],
                "your-user@your-server-ip": self.answers.get('remote_server', 'your-user@your-server-ip'),
                "/path/to/backups": self.answers.get('remote_backup_dir', '/path/to/backups'),
            }
        )
        
        # Make build.sh executable
        os.chmod(self.project_dir / "build.sh", 0o755)
        
        # Copy and fill CLAUDE.md
        self._process_template(
            script_dir / "templates" / "CLAUDE_TEMPLATE.md",
            self.project_dir / "CLAUDE.md",
            {
                "[YOUR PROJECT NAME]": self.answers['project_name'],
                "[Brief description of what this project does]": self.answers['project_description'],
                "[e.g., Healthcare, Aviation, Finance, E-commerce]": self.answers['domain'],
                "[Who uses this application]": self.answers['target_users'],
                "[Development/Beta/Production]": "Development",
                "[2-3 sentences describing the project's purpose and value proposition]": f"{self.answers['project_description']}. Built for {self.answers['target_users']} in the {self.answers['domain']} industry.",
                "[#hexcode]": self.answers['primary_color'],
                "[Professional/Modern/Friendly/etc.]": self.answers['design_style'].title(),
                "[0px/4px/8px/16px]": self.answers['border_radius'],
                "[project-name]": self.answers['project_name'],
                "[Date]": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        
        # Copy other templates
        # Copy documentation files (with error handling)
        docs_to_copy = [
            ("STYLE_GUIDE_TEMPLATE.md", "STYLE_GUIDE.md"),
            ("CODING_GUIDE_TEMPLATE.md", "CODING_GUIDE.md"),
            ("COMPLETE_BEGINNERS_GUIDE.md", "BEGINNERS_GUIDE.md"),
        ]

        for source_file, dest_file in docs_to_copy:
            source_path = script_dir / "templates" / source_file
            if source_path.exists():
                try:
                    shutil.copy(source_path, self.project_dir / "docs" / dest_file)
                    print(f"  ✅ Copied {dest_file}")
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not copy {source_file}: {e}")
            else:
                print(f"  ⚠️  Warning: {source_file} not found (skipping)")

        # Generate file handling guide
        self._generate_file_handling_guide()

        # Generate authentication guide (if auth is included)
        if self.answers.get('include_auth', True):
            self._generate_auth_guide()

        # Copy nginx configuration
        if (script_dir / "templates" / "docker" / "nginx.conf.template").exists():
            shutil.copy(script_dir / "templates" / "docker" / "nginx.conf.template", self.project_dir / "nginx" / "nginx.conf")
        if (script_dir / "templates" / "docker" / "nginx.Dockerfile.template").exists():
            shutil.copy(script_dir / "templates" / "docker" / "nginx.Dockerfile.template", self.project_dir / "nginx" / "Dockerfile")

        # Copy Makefile
        if (script_dir / "templates" / "config" / "Makefile.template").exists():
            self._process_template(
                script_dir / "templates" / "config" / "Makefile.template",
                self.project_dir / "Makefile",
                {"PROJECT_NAME": self.answers['project_name']}
            )

        # Copy pre-commit config (new ruff-based version)
        if (script_dir / "templates" / "config" / ".pre-commit-config.yaml.template").exists():
            shutil.copy(script_dir / "templates" / "config" / ".pre-commit-config.yaml.template", self.project_dir / ".pre-commit-config.yaml")

        # Copy pyproject.toml for tool configuration
        if (script_dir / "templates" / "config" / "pyproject.toml.template").exists():
            shutil.copy(script_dir / "templates" / "config" / "pyproject.toml.template", self.project_dir / "pyproject.toml")

        # Copy GitHub workflows
        workflows_dir = self.project_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        for workflow_file in ["ci.yml.template", "dependency-review.yml.template", "codeql.yml.template"]:
            workflow_path = script_dir / "templates" / ".github" / "workflows" / workflow_file
            if workflow_path.exists():
                output_name = workflow_file.replace(".template", "")
                shutil.copy(workflow_path, workflows_dir / output_name)
                # Replace PROJECT_NAME placeholder
                workflow_content = (workflows_dir / output_name).read_text()
                workflow_content = workflow_content.replace("{{PROJECT_NAME}}", self.answers['project_name'])
                (workflows_dir / output_name).write_text(workflow_content)
        
        # Create Django settings templates
        self._create_django_settings(script_dir)
        
        # Copy validation scripts
        if (script_dir / "validate_setup.py").exists():
            shutil.copy(script_dir / "validate_setup.py", self.project_dir / "validate_setup.py")
            os.chmod(self.project_dir / "validate_setup.py", 0o755)

        if (script_dir / "validate_deployment.py").exists():
            shutil.copy(script_dir / "validate_deployment.py", self.project_dir / "validate_deployment.py")
            os.chmod(self.project_dir / "validate_deployment.py", 0o755)

        # Update STYLE_GUIDE.md with answers
        self._fill_style_guide()

        # Copy share image and generate PWA files
        self._setup_share_image()
        self._generate_pwa_files()

        print("✅ Documentation generated")
    
    def _create_django_settings(self, script_dir: Path):
        """Create Django settings files from templates."""
        print("⚙️  Creating Django settings...")
        
        settings_dir = self.project_dir / "config" / "settings"
        settings_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py files
        (self.project_dir / "config" / "__init__.py").touch()
        (settings_dir / "__init__.py").touch()
        
        replacements = {
            "{{PROJECT_NAME}}": self.answers['project_name'],
            "{{PROJECT_NAME_SNAKE}}": self.answers['project_name_snake'],
            "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
            "{{DEV_DATABASE}}": self.answers['dev_database'],
            "{{DOMAIN_NAME}}": self.answers.get('domain_name', 'example.com'),
        }
        
        # Process Django settings templates
        settings_templates = [
            ('django-settings-base.py.template', 'base.py'),
            ('django-settings-development.py.template', 'development.py'),
            ('django-settings-production.py.template', 'production.py'),
        ]

        for template_name, output_name in settings_templates:
            template_path = script_dir / "templates" / "config" / "settings" / template_name
            if template_path.exists():
                self._process_template(
                    template_path,
                    settings_dir / output_name,
                    replacements
                )
                print(f"  ✅ Created {output_name}")
            else:
                print(f"  ⚠️  Template {template_name} not found")

        # Create config/urls.py
        self._create_urls_py()

        # Create config/wsgi.py
        self._create_wsgi_py()

        # Create config/asgi.py
        self._create_asgi_py()

        # Create manage.py
        self._create_manage_py()

        # Create core app with homepage
        self._create_core_app()

    def _create_manage_py(self):
        """Create manage.py that uses development settings by default."""
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
        print("  ✅ Created manage.py")

    def _create_core_app(self):
        """Create the core app with a basic homepage."""
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
        views_content = f'''"""
Core app views.
"""
from django.shortcuts import render


def home(request):
    """Homepage view."""
    context = {{
        'project_name': '{self.answers['project_name']}',
    }}
    return render(request, 'core/home.html', context)
'''
        (core_dir / "views.py").write_text(views_content)

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
        {% verbatim %}
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }

        .container {
            text-align: center;
            max-width: 600px;
        }

        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: fadeInUp 0.6s ease-out;
        }

        .emoji {
            font-size: 5rem;
            margin-bottom: 2rem;
            animation: bounce 1s ease-in-out infinite;
        }

        p {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.95;
            animation: fadeInUp 0.6s ease-out 0.2s both;
        }

        .info {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 2rem;
            margin-top: 2rem;
            animation: fadeInUp 0.6s ease-out 0.4s both;
        }

        .info h2 {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }

        .links {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 1.5rem;
        }

        .links a {
            color: white;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .links a:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        {% endverbatim %}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎉</div>
        <h1>You Made It!</h1>
        <p>{{ project_name }} is fully configured and ready to build</p>

        <div class="info">
            <h2>What You Have</h2>
            <p style="margin-bottom: 1.5rem; opacity: 0.9;">
                ✅ Django project with production-ready settings<br>
                ✅ Docker & GitHub Actions configured<br>
                ✅ Modern Python tools (ruff, pytest, pre-commit)<br>
                ✅ Health checks & monitoring ready
            </p>

            <h2 style="margin-top: 2rem;">Start Building</h2>
            <p style="margin-bottom: 1rem; opacity: 0.9;">
                Open your terminal and type your first prompt to AI to start building your project!
            </p>

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

        # Create models.py and admin.py to avoid Django warnings
        (core_dir / "models.py").write_text('from django.db import models\n\n# Create your models here.\n')
        (core_dir / "admin.py").write_text('from django.contrib import admin\n\n# Register your models here.\n')
        (core_dir / "apps.py").write_text(f'''from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
''')

        print("  ✅ Created core app with homepage")

    def _create_urls_py(self):
        """Create the main URL configuration."""
        config_dir = self.project_dir / "config"

        urls_content = f'''"""
URL configuration for {self.answers['project_name']} project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.core.urls')),  # Homepage and core views
    path('admin/', admin.site.urls),
'''

        # Add health check URLs if configured
        urls_content += "    path('health/', include('health_check.urls')),\n"

        # Add accounts URLs if authentication is included
        # (API URLs are included within apps.accounts.urls)
        if self.answers.get('include_auth', True):
            urls_content += "    path('accounts/', include('apps.accounts.urls')),\n"

        # Close urlpatterns and add static files
        urls_content += ''']

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Add browser auto-reload (only if installed and in INSTALLED_APPS)
    if 'django_browser_reload' in settings.INSTALLED_APPS:
        try:
            urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
        except Exception:
            pass

    # Add debug toolbar (only if installed and in INSTALLED_APPS)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        try:
            import debug_toolbar
            urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
        except Exception:
            pass
'''
        (config_dir / "urls.py").write_text(urls_content)
        print("  ✅ Created urls.py")

    def _create_wsgi_py(self):
        """Create WSGI configuration."""
        config_dir = self.project_dir / "config"

        wsgi_content = f'''"""
WSGI config for {self.answers['project_name']} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
'''
        (config_dir / "wsgi.py").write_text(wsgi_content)
        print("  ✅ Created wsgi.py")

    def _create_asgi_py(self):
        """Create ASGI configuration."""
        config_dir = self.project_dir / "config"

        asgi_content = f'''"""
ASGI config for {self.answers['project_name']} project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
'''
        (config_dir / "asgi.py").write_text(asgi_content)
        print("  ✅ Created asgi.py")

    def _process_template(self, source: Path, destination: Path, replacements: Dict[str, str]):
        """Process a template file with replacements."""
        content = source.read_text()
        
        for old, new in replacements.items():
            if new is None or (isinstance(new, str) and new.lower() in ['none', '']):
                new = old  # Keep the placeholder if value is None, empty, or "none"
            content = content.replace(old, new)
        
        destination.write_text(content)
    
    def _fill_style_guide(self):
        """Fill in the style guide with collected answers."""
        style_guide_path = self.project_dir / "docs" / "STYLE_GUIDE.md"
        content = style_guide_path.read_text()

        # Replace the questionnaire section with filled answers
        replacements = {
            "**Project Name**: _________________": f"**Project Name**: {self.answers['project_name']}",
            "**Primary Color**: #_________": f"**Primary Color**: {self.answers['primary_color']}",
            "**Secondary Color**: #_________": f"**Secondary Color**: {self.answers['secondary_color']}",
            "**Accent Color**: #_________": f"**Accent Color**: {self.answers['accent_color']}",
        }

        for old, new in replacements.items():
            content = content.replace(old, new)

        style_guide_path.write_text(content)

    def _setup_share_image(self):
        """Copy the share image to the project if provided."""
        if self.answers.get('share_image_path'):
            print("\n📸 Setting up share image...")
            source_path = self.answers['share_image_path']
            # Use the original extension
            ext = source_path.suffix
            dest_path = self.project_dir / "static" / "img" / f"default-share{ext}"

            try:
                shutil.copy(source_path, dest_path)
                print(f"  ✅ Copied share image to static/img/default-share{ext}")
                # Store the extension for later use in templates
                self.answers['share_image_ext'] = ext
            except Exception as e:
                print(f"  ⚠️  Warning: Could not copy image: {e}")
                self.answers['share_image_ext'] = None
        else:
            print("\n💡 No share image provided - you can add one later to static/img/default-share.jpg")
            self.answers['share_image_ext'] = None

    def _generate_file_handling_guide(self):
        """Generate comprehensive file handling documentation."""
        file_handling_content = f"""# File Handling Guide

## Overview

This guide covers best practices for handling file uploads in {self.answers['project_name']}, including user uploads, bulk data imports, and security considerations.

## Django Media Files Setup

Your project is already configured with:
- `MEDIA_ROOT`: Where uploaded files are stored
- `MEDIA_URL`: URL prefix for serving media files
- Docker volume mounting for persistent storage
- `.gitignore` excludes `media/` directory

## User-Uploaded Files (Images, Documents, PDFs)

### 1. Model Setup

```python
# apps/core/models.py
from django.db import models
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    \"\"\"Example model for file uploads.\"\"\"
    title = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    # File field with validation
    file = models.FileField(
        upload_to='documents/%Y/%m/',  # Organized by year/month
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
        ],
        help_text="Allowed: PDF, DOC, DOCX (max 10MB)"
    )

    # Image field (automatically validates image formats)
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(help_text="File size in bytes")

    def save(self, *args, **kwargs):
        # Store file size on save
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-uploaded_at']

class UserProfile(models.Model):
    \"\"\"Example for user avatar uploads.\"\"\"
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
```

### 2. Form Handling

```python
# apps/core/forms.py
from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'thumbnail']
        widgets = {{
            'file': forms.FileInput(attrs={{'accept': '.pdf,.doc,.docx'}}),
            'thumbnail': forms.FileInput(attrs={{'accept': 'image/*'}}),
        }}

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            # Validate file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")

            # Validate content type
            allowed_types = ['application/pdf', 'application/msword',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Invalid file type")

        return file
```

### 3. View Implementation

```python
# apps/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentUploadForm

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentUploadForm()

    return render(request, 'core/upload.html', {{'form': form}})
```

### 4. Template (Mobile-First)

```html
<!-- templates/core/upload.html -->
{{% extends 'base.html' %}}
{{% load static %}}

{{% block content %}}
<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>Upload Document</h2>
        </div>
        <div class="card-body">
            <form method="post" enctype="multipart/form-data">
                {{% csrf_token %}}

                <div class="form-group">
                    <label for="id_title" class="form-label">
                        Title <span class="required">*</span>
                    </label>
                    {{{{ form.title }}}}
                    {{% if form.title.errors %}}
                        <div class="form-errors">{{{{ form.title.errors }}}}</div>
                    {{% endif %}}
                </div>

                <div class="form-group">
                    <label for="id_file" class="form-label">
                        Document <span class="required">*</span>
                    </label>
                    {{{{ form.file }}}}
                    <div class="form-help">Allowed: PDF, DOC, DOCX (max 10MB)</div>
                    {{% if form.file.errors %}}
                        <div class="form-errors">{{{{ form.file.errors }}}}</div>
                    {{% endif %}}
                </div>

                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">Upload</button>
                    <a href="{{% url 'document_list' %}}" class="btn btn-outline">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{{% endblock %}}
```

## Bulk Data Import (CSV, Excel)

### CSV Import Example

```python
# apps/core/management/commands/import_data.py
import csv
from django.core.management.base import BaseCommand
from apps.core.models import YourModel

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)

            created_count = 0
            for row in reader:
                obj, created = YourModel.objects.get_or_create(
                    field1=row['column1'],
                    defaults={{
                        'field2': row['column2'],
                        'field3': row['column3'],
                    }}
                )
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {{created_count}} records')
            )

# Usage: python manage.py import_data data.csv
```

### Excel Import (with pandas)

```python
# Add to requirements/base.txt: pandas>=2.0.0 openpyxl>=3.1.0

import pandas as pd
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **options):
        df = pd.read_excel(options['excel_file'])

        for index, row in df.iterrows():
            YourModel.objects.create(
                field1=row['Column1'],
                field2=row['Column2'],
            )

        self.stdout.write(
            self.style.SUCCESS(f'Imported {{len(df)}} records')
        )
```

## Security Best Practices

### 1. File Validation

```python
# apps/core/validators.py
from django.core.exceptions import ValidationError
import magic  # pip install python-magic

def validate_file_type(file):
    \"\"\"Validate file type using magic numbers (not just extension).\"\"\"
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']

    # Read first 2048 bytes to detect file type
    file_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Reset file pointer

    if file_type not in allowed_types:
        raise ValidationError(f'Unsupported file type: {{file_type}}')

def validate_image_dimensions(image):
    \"\"\"Ensure image meets size requirements.\"\"\"
    if image.width > 4000 or image.height > 4000:
        raise ValidationError('Image dimensions too large (max 4000x4000)')

    if image.width < 100 or image.height < 100:
        raise ValidationError('Image dimensions too small (min 100x100)')
```

### 2. Virus Scanning (Production)

```python
# For production environments, consider ClamAV integration
# pip install clamd

import clamd

def scan_file_for_viruses(file):
    \"\"\"Scan uploaded file for viruses.\"\"\"
    cd = clamd.ClamdUnixSocket()

    # Scan file
    result = cd.instream(file)

    if result['stream'][0] == 'FOUND':
        raise ValidationError('File failed virus scan')
```

### 3. Secure File Storage

```python
# config/settings/base.py

# Generate random filenames to prevent directory traversal
import os
import uuid

def user_directory_path(instance, filename):
    \"\"\"Generate secure upload path.\"\"\"
    ext = filename.split('.')[-1]
    filename = f'{{uuid.uuid4()}}.{{ext}}'
    return os.path.join('user_{{0}}'.format(instance.user.id), filename)

# Use in model:
# file = models.FileField(upload_to=user_directory_path)
```

### 4. Serving Files Securely

```python
# apps/core/views.py
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
import os

@login_required
def serve_protected_file(request, document_id):
    \"\"\"Serve files only to authorized users.\"\"\"
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        raise Http404

    # Check permissions
    if document.uploaded_by != request.user and not request.user.is_staff:
        raise Http404

    # Serve file
    file_path = document.file.path
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(file_path)
        )

    raise Http404
```

## Image Processing

### Thumbnail Generation

```python
# pip install Pillow (already in requirements)

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def create_thumbnail(image_field, size=(300, 300)):
    \"\"\"Create thumbnail from uploaded image.\"\"\"
    img = Image.open(image_field)

    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    # Create thumbnail
    img.thumbnail(size, Image.Resampling.LANCZOS)

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)

    return InMemoryUploadedFile(
        output, 'ImageField',
        f"thumb_{{image_field.name}}",
        'image/jpeg',
        output.getbuffer().nbytes,
        None
    )

# Use in model save():
# if self.image and not self.thumbnail:
#     self.thumbnail = create_thumbnail(self.image)
```

## Cloud Storage (AWS S3)

### Setup for Production

```python
# pip install boto3 django-storages

# config/settings/production.py

INSTALLED_APPS += ['storages']

# AWS S3 Settings
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{{AWS_STORAGE_BUCKET_NAME}}.s3.amazonaws.com'

# Static/Media file storage
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Security
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {{
    'CacheControl': 'max-age=86400',
}}
```

## Testing File Uploads

```python
# tests/test_uploads.py
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.models import Document

class FileUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.client.login(username='test', password='password')

    def test_upload_valid_file(self):
        # Create fake file
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            file_content,
            content_type="application/pdf"
        )

        response = self.client.post('/upload/', {{
            'title': 'Test Document',
            'file': uploaded_file
        }})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 1)

    def test_upload_oversized_file(self):
        # Create file larger than 10MB
        large_file = SimpleUploadedFile(
            "large.pdf",
            b'x' * (11 * 1024 * 1024),  # 11MB
            content_type="application/pdf"
        )

        response = self.client.post('/upload/', {{
            'title': 'Large File',
            'file': large_file
        }})

        self.assertFormError(response, 'form', 'file', 'File size must be under 10MB')
```

## Domain-Specific Considerations

**For {self.answers['domain']} applications:**

{self._get_domain_file_handling_notes()}

## Checklist

- [ ] Models have appropriate FileField/ImageField validators
- [ ] Forms validate file size and type
- [ ] Views check user permissions before serving files
- [ ] Files stored with secure, random filenames
- [ ] Media files excluded from git (.gitignore)
- [ ] Docker volumes configured for media persistence
- [ ] Thumbnails generated for images (if needed)
- [ ] Consider virus scanning for production
- [ ] Plan for cloud storage (S3) if scaling

## Additional Resources

- [Django File Uploads](https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/)
- [Handling User Uploads](https://docs.djangoproject.com/en/5.0/ref/models/fields/#filefield)
- [django-storages Documentation](https://django-storages.readthedocs.io/)

---

*Generated for {self.answers['project_name']} on {datetime.now().strftime('%Y-%m-%d')}*
"""

        file_handling_path = self.project_dir / "docs" / "FILE_HANDLING.md"
        file_handling_path.write_text(file_handling_content)
        print("  ✅ Created file handling guide")

    def _get_domain_file_handling_notes(self) -> str:
        """Get domain-specific file handling recommendations."""
        domain = self.answers['domain'].lower()

        if 'aviation' in domain:
            return """
- **Pilot Certificates**: PDF uploads with OCR validation
- **Medical Certificates**: Secure storage with expiration tracking
- **Flight Logs**: CSV/Excel import for bulk data
- **Aircraft Photos**: Image validation and thumbnail generation
- **Maintenance Records**: Document retention requirements
"""
        elif 'healthcare' in domain or 'medical' in domain:
            return """
- **Patient Records**: HIPAA-compliant encrypted storage
- **Medical Images**: DICOM format support consideration
- **Lab Results**: PDF uploads with audit logging
- **Insurance Documents**: Secure access controls
- **Consent Forms**: Digital signature integration
"""
        elif 'finance' in domain or 'banking' in domain:
            return """
- **Financial Statements**: PDF validation and archival
- **Transaction Records**: CSV import with reconciliation
- **Tax Documents**: Secure storage with retention policies
- **Identity Verification**: Document scanning and validation
- **Audit Logs**: Immutable record-keeping
"""
        elif 'commerce' in domain or 'retail' in domain:
            return """
- **Product Images**: Multiple sizes/thumbnails generation
- **Product Data**: CSV/Excel import for inventory
- **Customer Receipts**: PDF generation and storage
- **Return Labels**: Dynamic PDF generation
- **Supplier Documents**: Organized by vendor
"""
        elif 'education' in domain:
            return """
- **Student Documents**: Transcripts, certificates
- **Assignment Submissions**: Multiple format support
- **Course Materials**: PDF, video, presentations
- **Grades Import**: CSV bulk import
- **Certificates**: Automated PDF generation
"""
        else:
            return """
- Consider what types of files users will upload
- Plan for file retention and cleanup policies
- Determine access control requirements
- Consider backup and disaster recovery
- Plan for file format conversions if needed
"""

    def _generate_auth_guide(self):
        """Generate comprehensive authentication setup guide."""
        login_method = self.answers.get('login_method', 'email')
        auth_type = self.answers.get('auth_type', 'hybrid')
        enable_2fa = self.answers.get('enable_2fa', False)

        auth_guide_content = f"""# Authentication Setup Guide

## Overview

Your {self.answers['project_name']} project includes a complete authentication system with:
- **Custom User Model** (can't be added later!)
- **Login Method**: {login_method.title()}
- **Auth Type**: {auth_type.title()} {'(Web + API)' if auth_type == 'hybrid' else ''}
{'- **Two-Factor Authentication**: Enabled ✓' if enable_2fa else ''}
- **Email Verification**: {'Enabled ✓' if self.answers.get('email_verification') else 'Disabled'}
- **Password Strength**: Django validators enabled

## Quick Start

### 1. Run Migrations (Creates User Table)

```bash
# Create migration files for your custom User model
python manage.py makemigrations accounts

# Apply all migrations
python manage.py migrate
```

This creates the `users` table in your database.

### 2. Create Your First Superuser

```bash
python manage.py createsuperuser
```

**What you'll be asked:**
- **{"Email" if login_method == 'email' else "Username"}**: Your login identifier
{'- **Username**: For the admin (required by Django)' if login_method == 'email' else '- **Email**: Your email address'}
- **Password**: Must meet these requirements:
  - Minimum 8 characters
  - Can't be too similar to your {"email" if login_method == 'email' else "username"}
  - Can't be a common password (like "password123")
  - Can't be entirely numeric

**Example:**
```
{"Email address" if login_method == 'email' else "Username"}: {"admin@example.com" if login_method == 'email' else "admin"}
{'Username: admin' if login_method == 'email' else 'Email address: admin@example.com'}
Password: ********
Password (again): ********
Superuser created successfully!
```

**💡 Password Tips:**
- Use a passphrase: `BlueSky-Mountain-42!`
- Mix letters, numbers, symbols
- Store in password manager (1Password, LastPass, Bitwarden)

### 3. Test Your Setup

**Start the dev server:**
```bash
python manage.py runserver
```

**Web Login** (if using web/hybrid):
- Go to: http://localhost:8000/accounts/login/
- Login with your superuser credentials
- Access admin: http://localhost:8000/admin/

**API Login** (if using api/hybrid):
```bash
# Get JWT tokens
curl -X POST http://localhost:8000/api/auth/token/ \\
  -H "Content-Type: application/json" \\
  -d '{{"{"email" if login_method == "email" else "username"}": "{"admin@example.com" if login_method == "email" else "admin"}", "password": "your-password"}}'

# Response:
{{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}}

# Use token in subsequent requests
curl http://localhost:8000/api/auth/me/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Custom User Model Details

### Location: `apps/accounts/models.py`

Your custom User model extends Django's `AbstractUser` and adds:

```python
class User(AbstractUser):
    # Login field
    USERNAME_FIELD = '{login_method}'  # Users log in with {'email' if login_method == 'email' else 'username'}

    # Additional fields
    email = models.EmailField(unique=True)  # Always unique
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    email_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Adding Custom Fields

Want to add more fields? Edit `apps/accounts/models.py`:

```python
class User(AbstractUser):
    # ... existing fields ...

    # Your custom fields
    date_of_birth = models.DateField(null=True, blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
```

**Then create and run migration:**
```bash
python manage.py makemigrations accounts -m "Add custom user fields"
python manage.py migrate
```

## Available Endpoints

### Web Endpoints (Browser)

- **Login**: `/accounts/login/`
- **Logout**: `/accounts/logout/`
- **Register**: `/accounts/register/`
- **Profile**: `/accounts/profile/`
- **Password Reset**: `/accounts/password-reset/`
- **Password Change**: `/accounts/password-change/`

### API Endpoints (JSON)

- **Register**: `POST /api/auth/register/`
- **Get Token**: `POST /api/auth/token/`
- **Refresh Token**: `POST /api/auth/token/refresh/`
- **Current User**: `GET /api/auth/me/`

## Password Requirements Explained

Django includes these validators by default (configured in `settings/base.py`):

### 1. UserAttributeSimilarityValidator
❌ **Bad**: If username is "john", password can't be "john123"
✅ **Good**: Password is different from username/email

### 2. MinimumLengthValidator
❌ **Bad**: "pass123" (too short)
✅ **Good**: At least 8 characters

### 3. CommonPasswordValidator
❌ **Bad**: "password", "123456", "qwerty"
✅ **Good**: Not in list of 20,000 common passwords

### 4. NumericPasswordValidator
❌ **Bad**: "12345678" (all numbers)
✅ **Good**: Mix of letters and numbers

**Adjust in `settings/base.py` if needed:**
```python
AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {{'min_length': 12}}  # Require 12 characters instead of 8
    }},
    # ... other validators
]
```

## Creating Regular Users

### Via Web Interface
Users can self-register at `/accounts/register/`

### Via Django Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create regular user
user = User.objects.create_user(
    {'email' if login_method == 'email' else 'username'}='{"user@example.com" if login_method == 'email' else "johndoe"}',
    {'username' if login_method == 'email' else 'email'}='{"johndoe" if login_method == 'email' else "johndoe@example.com"}',
    password='SecurePass123!',
    first_name='John',
    last_name='Doe'
)

# Create staff user (can access admin)
staff = User.objects.create_user(
    {'email' if login_method == 'email' else 'username'}='{"staff@example.com" if login_method == 'email' else "staff"}',
    password='SecurePass123!',
    is_staff=True  # Can access admin
)
```

### Via Management Command (Bulk Import)
```bash
# Create: apps/accounts/management/commands/create_users.py
python manage.py create_users users.csv
```

## Authentication in Views

### Web Views (Function-Based)
```python
from django.contrib.auth.decorators import login_required

@login_required  # Redirects to /accounts/login/ if not logged in
def my_view(request):
    user = request.user  # Current logged-in user
    return render(request, 'my_template.html', {{'user': user}})
```

### Web Views (Class-Based)
```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class MyView(LoginRequiredMixin, TemplateView):
    template_name = 'my_template.html'
    login_url = '/accounts/login/'  # Optional: custom login URL
```

### API Views
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requires JWT token
def my_api_view(request):
    user = request.user  # User from JWT token
    return Response({{'message': f'Hello, {{user.email}}'}})
```

## Testing Authentication

### Test User Creation
```python
# tests/test_auth.py
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

class AuthTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            {'email' if login_method == 'email' else 'username'}='{"test@example.com" if login_method == 'email' else "testuser"}',
            password='TestPass123!'
        )
        self.assertEqual(user.{'email' if login_method == 'email' else 'username'}, '{"test@example.com" if login_method == 'email' else "testuser"}')
        self.assertTrue(user.check_password('TestPass123!'))
```

### Test Login
```python
def test_login(self):
    # Create user
    user = User.objects.create_user(
        {'email' if login_method == 'email' else 'username'}='{"test@example.com" if login_method == 'email' else "testuser"}',
        password='TestPass123!'
    )

    # Test login
    logged_in = self.client.login(
        {'email' if login_method == 'email' else 'username'}='{"test@example.com" if login_method == 'email' else "testuser"}',
        password='TestPass123!'
    )
    self.assertTrue(logged_in)
```

## Troubleshooting

### "No such table: users"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### "Superuser must have is_superuser=True"
**Solution**: Use `create_superuser()` not `create_user()`
```python
User.objects.create_superuser(...)  # ✓ Correct
```

### "Password doesn't meet requirements"
**Solution**: Make password stronger (8+ chars, not common, not all numbers)

### "Email already exists" (when using email login)
**Solution**: Each email must be unique. Use different email or delete existing user:
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(email='duplicate@example.com').delete()
```

### JWT Token Invalid/Expired
**Solution**: Get new token or use refresh token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \\
  -H "Content-Type: application/json" \\
  -d '{{"refresh": "YOUR_REFRESH_TOKEN"}}'
```

## Security Best Practices

✅ **DO**:
- Store .env file securely (already gitignored)
- Use strong SECRET_KEY (automatically generated)
- Enable HTTPS in production
- Use environment-specific settings (development.py vs production.py)
- Rotate JWT tokens regularly
- Log authentication attempts

❌ **DON'T**:
- Commit .env to git (already prevented)
- Use DEBUG=True in production
- Store passwords in plain text
- Share SECRET_KEY publicly
- Use default Django SECRET_KEY

## Production Checklist

Before deploying:

- [ ] Set `DEBUG=False` in .env
- [ ] Configure proper `ALLOWED_HOSTS` in .env
- [ ] Set up SMTP for email (password reset)
- [ ] Enable HTTPS
- [ ] Configure CORS for your frontend domain
- [ ] Set up proper logging/monitoring
- [ ] Test password reset flow
- [ ] Test JWT token expiration
{'- [ ] Configure 2FA (TOTP apps: Google Authenticator, Authy)' if enable_2fa else ''}

## Additional Resources

- [Django Authentication Docs](https://docs.djangoproject.com/en/5.0/topics/auth/)
- [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

*Generated for {self.answers['project_name']} on {datetime.now().strftime('%Y-%m-%d')}*
*Login method: {login_method} | Auth type: {auth_type}*
"""

        auth_guide_path = self.project_dir / "docs" / "AUTH_SETUP.md"
        auth_guide_path.write_text(auth_guide_content)
        print("  ✅ Created authentication setup guide")

    def _generate_pwa_files(self):
        """Generate PWA manifest and service worker files."""
        print("\n📱 Generating PWA files...")


        # Determine the image filename and type
        if self.answers.get('share_image_ext'):
            share_image = f"/static/img/default-share{self.answers['share_image_ext']}"
            image_ext = self.answers['share_image_ext'].lstrip('.')
        else:
            share_image = "/static/img/default-share.jpg"
            image_ext = "jpg"

        # Convert jpg to jpeg for mime type
        image_type = image_ext.replace('jpg', 'jpeg')

        # Generate manifest.json
        manifest = {
            "name": self.answers['project_name'].replace('-', ' ').title(),
            "short_name": self.answers['project_name'].replace('-', ' ').title(),
            "description": self.answers['project_description'],
            "start_url": "/",
            "display": "standalone",
            "background_color": self.answers['primary_color'],
            "theme_color": self.answers['primary_color'],
            "icons": [
                {
                    "src": share_image,
                    "sizes": "512x512",
                    "type": f"image/{image_type}"
                }
            ]
        }

        import json
        manifest_path = self.project_dir / "static" / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print("  ✅ Created PWA manifest.json")

        # Generate basic service worker
        service_worker = """// Service Worker for PWA
const CACHE_NAME = 'v1';
const urlsToCache = [
  '/',
  '/static/css/base.css',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
"""

        service_worker_path = self.project_dir / "static" / "js" / "service-worker.js"
        service_worker_path.write_text(service_worker)
        print("  ✅ Created service-worker.js")

        # Create a note about PWA setup
        pwa_note = f"""# PWA & Open Graph Setup

## Files Generated

- `static/manifest.json` - PWA manifest
- `static/js/service-worker.js` - Basic service worker
{f"- `static/img/default-share{self.answers.get('share_image_ext')}` - Default share image" if self.answers.get('share_image_ext') else ""}

## Add to base.html

```html
<head>
    <!-- PWA Manifest -->
    <link rel="manifest" href="{{% static 'manifest.json' %}}">
    <meta name="theme-color" content="{self.answers['primary_color']}">

    <!-- Open Graph with defaults -->
    <meta property="og:title" content="{{% block og_title %}}{self.answers['project_name'].title()}{{% endblock %}}">
    <meta property="og:description" content="{{% block og_description %}}{self.answers['project_description']}{{% endblock %}}">
    <meta property="og:image" content="{{% block og_image %}}{{{{ request.scheme }}}}://{{{{ request.get_host }}}}{{% static 'img/default-share{self.answers.get('share_image_ext') or '.jpg'}' %}}{{% endblock %}}">
    <meta property="og:url" content="{{{{ request.build_absolute_uri }}}}">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{{% block twitter_image %}}{{{{ request.scheme }}}}://{{{{ request.get_host }}}}{{% static 'img/default-share{self.answers.get('share_image_ext') or '.jpg'}' %}}{{% endblock %}}">

    <!-- Apple Touch Icon -->
    <link rel="apple-touch-icon" href="{{% static 'img/default-share{self.answers.get('share_image_ext') or '.jpg'}' %}}">
</head>
```

## Register Service Worker

Add before closing `</body>` tag:

```html
<script>
if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('{{% static 'js/service-worker.js' %}}');
}}
</script>
```

## Image Recommendations

- **Open Graph**: 1200x630px (1.91:1 ratio)
- **PWA Icons**: 512x512px (square)
- **Format**: PNG or JPG
- **Size**: Under 1MB

{f"✅ Your image has been copied to: static/img/default-share{self.answers.get('share_image_ext')}" if self.answers.get('share_image_ext') else "⚠️  No image provided yet. Add your default share image to: static/img/default-share.jpg"}
"""

        pwa_note_path = self.project_dir / "docs" / "PWA_SETUP.md"
        pwa_note_path.write_text(pwa_note)
        print("  ✅ Created PWA setup guide in docs/PWA_SETUP.md")
    
    def generate_css(self):
        """Generate base.css from theme answers."""
        print("\n🎨 Generating CSS theme...")
        
        # Shadow values based on style
        shadow_values = {
            "none": ("none", "none", "none"),
            "subtle": (
                "0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)",
                "0 0.25rem 0.5rem rgba(0, 0, 0, 0.1)",
                "0 0.5rem 1rem rgba(0, 0, 0, 0.15)"
            ),
            "medium": (
                "0 0.25rem 0.5rem rgba(0, 0, 0, 0.1)",
                "0 0.5rem 1rem rgba(0, 0, 0, 0.15)",
                "0 1rem 2rem rgba(0, 0, 0, 0.2)"
            ),
            "strong": (
                "0 0.5rem 1rem rgba(0, 0, 0, 0.15)",
                "0 1rem 2rem rgba(0, 0, 0, 0.2)",
                "0 2rem 4rem rgba(0, 0, 0, 0.25)"
            ),
        }
        
        shadows = shadow_values.get(self.answers['shadow_style'], shadow_values['subtle'])
        
        css_content = f"""/* Generated Theme - {self.answers['project_name']} */
/* Generated on {datetime.now().strftime('%Y-%m-%d')} */

:root {{
    /* Brand Colors */
    --primary-color: {self.answers['primary_color']};
    --secondary-color: {self.answers['secondary_color']};
    --accent-color: {self.answers['accent_color']};
    
    /* Semantic Colors */
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
    
    /* Neutral Colors */
    --white: #ffffff;
    --gray-100: #f8f9fa;
    --gray-200: #e9ecef;
    --gray-300: #dee2e6;
    --gray-400: #ced4da;
    --gray-500: #adb5bd;
    --gray-600: #6c757d;
    --gray-700: #495057;
    --gray-800: #343a40;
    --gray-900: #212529;
    --black: #000000;
    
    /* Light Theme (default) */
    --bg-primary: var(--white);
    --bg-secondary: var(--gray-100);
    --bg-tertiary: var(--gray-200);
    --text-primary: var(--gray-900);
    --text-secondary: var(--gray-600);
    --text-muted: var(--gray-500);
    --border-color: var(--gray-300);
    
    /* Spacing System */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-xxl: 3rem;
    
    /* Typography */
    --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                        "Helvetica Neue", Arial, sans-serif;
    --font-family-mono: SFMono-Regular, Menlo, Monaco, Consolas, 
                        "Liberation Mono", "Courier New", monospace;
    
    /* Borders */
    --border-radius: {self.answers['border_radius']};
    --border-width: 1px;
    
    /* Shadows */
    --shadow-sm: {shadows[0]};
    --shadow-md: {shadows[1]};
    --shadow-lg: {shadows[2]};
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-base: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
    
    /* Z-index Scale */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;
    
    /* Mobile-First Sizing */
    --touch-target: 44px;
    --button-height: 44px;
    --input-height: 44px;
}}
"""

        if self.answers['dark_mode']:
            css_content += """
/* Dark Theme */
[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --bg-tertiary: #3a3a3a;
    --text-primary: #f0f0f0;
    --text-secondary: #b0b0b0;
    --text-muted: #808080;
    --border-color: #404040;
    
    /* Adjust shadows for dark mode */
    --shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.2);
    --shadow-md: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 0.5rem 1rem rgba(0, 0, 0, 0.4);
}
"""

        css_content += """
/* CSS Reset */
*, *::before, *::after {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: var(--font-family-base);
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-primary);
    background-color: var(--bg-primary);
    -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
}

/* Typography - Mobile First */
h1, h2, h3, h4, h5, h6 {
    margin-top: 0;
    margin-bottom: var(--spacing-md);
    font-weight: 600;
    line-height: 1.2;
    color: var(--text-primary);
}

h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }
h4 { font-size: 1.125rem; }
h5 { font-size: 1rem; }
h6 { font-size: 0.875rem; }

/* Larger headings on desktop */
@media (min-width: 768px) {
    h1 { font-size: 2.5rem; }
    h2 { font-size: 2rem; }
    h3 { font-size: 1.75rem; }
    h4 { font-size: 1.5rem; }
    h5 { font-size: 1.25rem; }
    h6 { font-size: 1rem; }
}

/* Links */
a {
    color: var(--primary-color);
    text-decoration: none;
    transition: color var(--transition-fast);
}

a:hover {
    color: var(--primary-color);
    opacity: 0.8;
}

/* Container */
.container {
    width: 100%;
    padding-right: var(--spacing-md);
    padding-left: var(--spacing-md);
    margin-right: auto;
    margin-left: auto;
}

@media (min-width: 576px) {
    .container { max-width: 540px; }
}

@media (min-width: 768px) {
    .container { max-width: 720px; }
}

@media (min-width: 992px) {
    .container { max-width: 960px; }
}

@media (min-width: 1200px) {
    .container { max-width: 1140px; }
}

/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.text-primary { color: var(--primary-color) !important; }
.text-secondary { color: var(--text-secondary) !important; }
.text-muted { color: var(--text-muted) !important; }

.bg-primary { background-color: var(--bg-primary) !important; }
.bg-secondary { background-color: var(--bg-secondary) !important; }

/* Spacing utilities */
.mt-0 { margin-top: 0 !important; }
.mt-1 { margin-top: var(--spacing-xs) !important; }
.mt-2 { margin-top: var(--spacing-sm) !important; }
.mt-3 { margin-top: var(--spacing-md) !important; }
.mt-4 { margin-top: var(--spacing-lg) !important; }
.mt-5 { margin-top: var(--spacing-xl) !important; }

.mb-0 { margin-bottom: 0 !important; }
.mb-1 { margin-bottom: var(--spacing-xs) !important; }
.mb-2 { margin-bottom: var(--spacing-sm) !important; }
.mb-3 { margin-bottom: var(--spacing-md) !important; }
.mb-4 { margin-bottom: var(--spacing-lg) !important; }
.mb-5 { margin-bottom: var(--spacing-xl) !important; }

.p-0 { padding: 0 !important; }
.p-1 { padding: var(--spacing-xs) !important; }
.p-2 { padding: var(--spacing-sm) !important; }
.p-3 { padding: var(--spacing-md) !important; }
.p-4 { padding: var(--spacing-lg) !important; }
.p-5 { padding: var(--spacing-xl) !important; }

/* Display utilities */
.d-none { display: none !important; }
.d-block { display: block !important; }
.d-inline-block { display: inline-block !important; }
.d-flex { display: flex !important; }

/* Responsive utilities */
@media (min-width: 768px) {
    .d-md-none { display: none !important; }
    .d-md-block { display: block !important; }
    .d-md-flex { display: flex !important; }
}

/* Accessibility */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Focus styles */
:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Mobile-first components will be added in component files */
"""
        
        # Write base.css
        css_path = self.project_dir / "static" / "css" / "base.css"
        css_path.write_text(css_content)
        
        # Create component CSS files
        self._create_component_css()
        
        print("✅ CSS theme generated")
    
    def _create_component_css(self):
        """Create component CSS files."""
        # Buttons component
        buttons_css = f"""/* Button Component - {self.answers['project_name']} */

.btn {{
    /* Base button styles - mobile first */
    display: inline-block;
    font-family: var(--font-family-base);
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    user-select: none;
    border: 1px solid transparent;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    line-height: 1.5;
    border-radius: var(--border-radius);
    transition: all var(--transition-base);
    cursor: pointer;
    
    /* Mobile-first sizing */
    min-height: var(--touch-target);
    min-width: var(--touch-target);
}}

/* Focus state for accessibility */
.btn:focus {{
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}}

/* Primary button */
.btn-primary {{
    color: var(--white);
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}}

.btn-primary:hover:not(:disabled) {{
    background-color: var(--primary-color);
    filter: brightness(90%);
}}

/* Secondary button */
.btn-secondary {{
    color: var(--white);
    background-color: var(--secondary-color);
    border-color: var(--secondary-color);
}}

.btn-secondary:hover:not(:disabled) {{
    background-color: var(--secondary-color);
    filter: brightness(90%);
}}

/* Outline variant */
.btn-outline {{
    color: var(--primary-color);
    background-color: transparent;
    border-color: var(--primary-color);
}}

.btn-outline:hover:not(:disabled) {{
    color: var(--white);
    background-color: var(--primary-color);
}}

/* Disabled state */
.btn:disabled {{
    opacity: 0.5;
    cursor: not-allowed;
}}

/* Button sizes */
.btn-sm {{
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    min-height: 36px;
}}

.btn-lg {{
    padding: 1rem 2rem;
    font-size: 1.125rem;
    min-height: 52px;
}}

/* Button group - stacks on mobile */
.btn-group {{
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}}

.btn-group .btn {{
    width: 100%;
}}

/* Horizontal on desktop */
@media (min-width: 768px) {{
    .btn {{
        padding: 0.5rem 1rem;
        min-height: auto;
    }}
    
    .btn-group {{
        flex-direction: row;
    }}
    
    .btn-group .btn {{
        width: auto;
    }}
}}
"""
        
        (self.project_dir / "static" / "css" / "components" / "buttons.css").write_text(buttons_css)
        
        # Forms component
        forms_css = """/* Form Component - Mobile First */

.form-group {
    margin-bottom: var(--spacing-md);
}

.form-label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
    color: var(--text-primary);
}

.form-control {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-primary);
    background-color: var(--bg-primary);
    background-clip: padding-box;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    
    /* Mobile-friendly sizing */
    min-height: var(--input-height);
}

.form-control:focus {
    color: var(--text-primary);
    background-color: var(--bg-primary);
    border-color: var(--primary-color);
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(var(--primary-color), 0.25);
}

.form-control::placeholder {
    color: var(--text-muted);
    opacity: 1;
}

/* Form validation states */
.form-group--error .form-control {
    border-color: var(--danger-color);
}

.form-group--error .form-control:focus {
    box-shadow: 0 0 0 0.2rem rgba(var(--danger-color), 0.25);
}

.form-errors {
    display: block;
    margin-top: var(--spacing-xs);
    font-size: 0.875rem;
    color: var(--danger-color);
}

.form-help {
    display: block;
    margin-top: var(--spacing-xs);
    font-size: 0.875rem;
    color: var(--text-muted);
}

/* Required indicator */
.required {
    color: var(--danger-color);
}

/* Responsive adjustments */
@media (min-width: 768px) {
    .form-control {
        padding: 0.5rem 0.75rem;
    }
}
"""
        
        (self.project_dir / "static" / "css" / "components" / "forms.css").write_text(forms_css)
        
        # Cards component
        cards_css = f"""/* Card Component */

.card {{
    position: relative;
    display: flex;
    flex-direction: column;
    min-width: 0;
    word-wrap: break-word;
    background-color: var(--bg-secondary);
    background-clip: border-box;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--spacing-md);
}}

.card-header {{
    padding: var(--spacing-md);
    background-color: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-color);
    border-radius: calc(var(--border-radius) - 1px) calc(var(--border-radius) - 1px) 0 0;
}}

.card-header h3,
.card-header h4 {{
    margin-bottom: 0;
}}

.card-body {{
    flex: 1 1 auto;
    padding: var(--spacing-md);
}}

.card-footer {{
    padding: var(--spacing-md);
    background-color: var(--bg-tertiary);
    border-top: 1px solid var(--border-color);
    border-radius: 0 0 calc(var(--border-radius) - 1px) calc(var(--border-radius) - 1px);
}}

/* Card variations based on design style */
{'/* Extra styling for ' + self.answers['design_style'] + ' design */' if self.answers['design_style'] else ''}
"""
        
        (self.project_dir / "static" / "css" / "components" / "cards.css").write_text(cards_css)

    def generate_env_file(self):
        """Generate .env file with secure secrets."""
        print("\n🔐 Generating .env with secure secrets...")

        # Generate secure keys
        import secrets
        import string

        def generate_secret_key():
            """Generate a Django-compatible SECRET_KEY."""
            chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
            return ''.join(secrets.choice(chars) for _ in range(50))

        def generate_password():
            """Generate a strong database password."""
            chars = string.ascii_letters + string.digits
            return ''.join(secrets.choice(chars) for _ in range(32))

        env_content = f"""# Django Settings
# SECURITY WARNING: Keep these secret!
SECRET_KEY={generate_secret_key()}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development)
DB_NAME={self.answers['project_name_snake']}_db
DB_USER={self.answers['project_name_snake']}_user
DB_PASSWORD={generate_password()}
DB_HOST=db
DB_PORT=5432

# Email Configuration
# Development: Prints to console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Production: Uncomment and configure SMTP
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@example.com
# EMAIL_HOST_PASSWORD=your-app-specific-password

# From Email
DEFAULT_FROM_EMAIL={self.answers['project_name']}@example.com

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
"""

        if self.answers.get('use_redis'):
            env_content += "\n# Redis\nREDIS_URL=redis://redis:6379/0\n"

        if self.answers.get('use_celery'):
            env_content += "\n# Celery\nCELERY_BROKER_URL=redis://redis:6379/0\n"

        if self.answers.get('use_sentry'):
            env_content += "\n# Sentry (add your DSN)\nSENTRY_DSN=\n"

        if self.answers.get('enable_2fa'):
            env_content += "\n# Two-Factor Authentication\nOTP_TOTP_ISSUER={self.answers['project_name']}\n"

        if self.answers.get('use_cloudflare'):
            env_content += f"""
# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=your-tunnel-token-here
DOMAIN_NAME={self.answers.get('domain_name', 'example.com')}
"""

        # Production settings reminder
        env_content += """
# Production Settings (update for deployment)
# DEBUG=False
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# Configure production email backend above
# Add production database credentials
"""

        # Write .env file
        (self.project_dir / ".env").write_text(env_content)
        print("  ✅ Generated .env with secure SECRET_KEY and database password")
        print("  ⚠️  IMPORTANT: .env is gitignored - never commit secrets to git!")

    def generate_auth_system(self):
        """Generate complete authentication system (custom User + hybrid auth)."""
        print("\n👤 Generating authentication system...")

        # Create accounts app directory
        accounts_dir = self.project_dir / "apps" / "accounts"
        accounts_dir.mkdir(parents=True, exist_ok=True)
        (accounts_dir / "__init__.py").touch()

        # Create migrations folder
        migrations_dir = accounts_dir / "migrations"
        migrations_dir.mkdir(exist_ok=True)
        (migrations_dir / "__init__.py").touch()

        # Determine login field
        login_method = self.answers.get('login_method', 'email')
        use_email_login = login_method in ['email', 'both']
        use_username_login = login_method in ['username', 'both']

        # 1. Generate Custom User Model
        self._generate_custom_user_model(accounts_dir, login_method)

        # 2. Generate Web Auth (forms, views, templates)
        if self.answers.get('auth_type') in ['web', 'hybrid']:
            self._generate_web_auth(accounts_dir)

        # 3. Generate API Auth (serializers, views)
        if self.answers.get('auth_type') in ['api', 'hybrid']:
            self._generate_api_auth(accounts_dir)

        # 4. Generate URLs
        self._generate_auth_urls(accounts_dir)

        print("  ✅ Custom User model created")
        print(f"  ✅ Login method: {login_method}")
        if self.answers.get('enable_2fa'):
            print("  ✅ Two-factor authentication configured")
        print(f"  ✅ Auth type: {self.answers.get('auth_type', 'hybrid')}")

    def _generate_custom_user_model(self, accounts_dir: Path, login_method: str):
        """Generate custom User model."""
        username_field = 'email' if login_method == 'email' else 'username'

        models_content = f'''"""
Custom User model for {self.answers['project_name']}.
Generated by Django Project Setup Wizard.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    Uses {'email' if login_method == 'email' else 'username'} as the unique identifier for authentication.
    """
    # Make email unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={{
            'unique': _("A user with that email already exists."),
        }},
    )

    # Additional fields
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # Set login field
    USERNAME_FIELD = '{username_field}'
'''

        if login_method == 'email':
            models_content += "    REQUIRED_FIELDS = ['username']  # For createsuperuser command\n"
        else:
            models_content += "    REQUIRED_FIELDS = ['email']  # For createsuperuser command\n"

        models_content += '''
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        '''

        if login_method == 'email':
            models_content += "return self.email\n"
        else:
            models_content += "return self.username\n"

        models_content += '''
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{{self.first_name}} {{self.last_name}}".strip()
        return full_name or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
'''

        # Write models.py
        (accounts_dir / "models.py").write_text(models_content)

        # Create admin.py
        admin_content = f'''"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""

    list_display = ['{"email" if login_method == "email" else "username"}', 'first_name', 'last_name', 'is_staff', 'email_verified', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'email_verified', 'date_joined']
    search_fields = ['{"email" if login_method == "email" else "username"}', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {{'fields': ('{"email" if login_method == "email" else "username"}', 'password')}}),
        (_('Personal info'), {{'fields': ('first_name', 'last_name', {"'email', " if login_method != 'email' else ""}'phone_number', 'avatar')}}),
        (_('Permissions'), {{
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }}),
        (_('Important dates'), {{'fields': ('last_login', 'date_joined')}}),
        (_('Verification'), {{'fields': ('email_verified',)}}),
    )

    add_fieldsets = (
        (None, {{
            'classes': ('wide',),
            'fields': ('{"email" if login_method == "email" else "username"}', {"'email', " if login_method != 'email' else ""}'password1', 'password2'),
        }}),
    )
'''

        (accounts_dir / "admin.py").write_text(admin_content)

    def _generate_web_auth(self, accounts_dir: Path):
        """Generate web authentication (forms, views, templates)."""
        # Create forms.py
        login_method = self.answers.get('login_method', 'email')

        forms_content = f'''"""
Authentication forms for {self.answers['project_name']}.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(
        label='{"Email" if login_method == "email" else "Username"}',
        widget=forms.TextInput(attrs={{
            'class': 'form-control',
            'placeholder': '{"your@email.com" if login_method == "email" else "username"}',
            'autofocus': True
        }})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={{
            'class': 'form-control',
            'placeholder': 'Password'
        }})
    )


class UserRegistrationForm(UserCreationForm):
    """Custom registration form."""
    {"email" if login_method != "email" else "username"} = forms.{"EmailField" if login_method != "email" else "CharField"}(
        required=True,
        widget=forms.{"EmailInput" if login_method != "email" else "TextInput"}(attrs={{'class': 'form-control'}})
    )

    class Meta:
        model = User
        fields = ('{"email" if login_method == "email" else "username"}', {"'email', " if login_method != 'email' else ""}'password1', 'password2')
        widgets = {{
            '{"email" if login_method == "email" else "username"}': forms.{"EmailInput" if login_method == "email" else "TextInput"}(attrs={{'class': 'form-control'}}),
        }}
'''

        (accounts_dir / "forms.py").write_text(forms_content)

        # Create views.py (basic auth views)
        views_content = '''"""
Authentication views for web interface.
"""
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserRegistrationForm, UserLoginForm


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'accounts/profile.html')
'''

        (accounts_dir / "views.py").write_text(views_content)

        # Create templates
        templates_dir = accounts_dir / "templates" / "accounts"
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Login template
        login_template = '''{% extends "base.html" %}
{% load static %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="container">
    <div class="card" style="max-width: 500px; margin: 2rem auto;">
        <div class="card-header">
            <h2>Login</h2>
        </div>
        <div class="card-body">
            <form method="post">
                {% csrf_token %}

                {% if form.non_field_errors %}
                    <div class="form-errors">
                        {{ form.non_field_errors }}
                    </div>
                {% endif %}

                <div class="form-group">
                    <label for="{{ form.username.id_for_label }}" class="form-label">
                        {{ form.username.label }}
                    </label>
                    {{ form.username }}
                    {% if form.username.errors %}
                        <div class="form-errors">{{ form.username.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-group">
                    <label for="{{ form.password.id_for_label }}" class="form-label">
                        {{ form.password.label }}
                    </label>
                    {{ form.password }}
                    {% if form.password.errors %}
                        <div class="form-errors">{{ form.password.errors }}</div>
                    {% endif %}
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>

                <div style="margin-top: 1rem; text-align: center;">
                    <a href="{% url 'password_reset' %}">Forgot password?</a> |
                    <a href="{% url 'register' %}">Create account</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''
        (templates_dir / "login.html").write_text(login_template)

        # Register template
        register_template = '''{% extends "base.html" %}
{% load static %}

{% block title %}Register{% endblock %}

{% block content %}
<div class="container">
    <div class="card" style="max-width: 500px; margin: 2rem auto;">
        <div class="card-header">
            <h2>Create Account</h2>
        </div>
        <div class="card-body">
            <form method="post">
                {% csrf_token %}

                {% for field in form %}
                    <div class="form-group">
                        <label for="{{ field.id_for_label }}" class="form-label">
                            {{ field.label }}
                            {% if field.field.required %}<span class="required">*</span>{% endif %}
                        </label>
                        {{ field }}
                        {% if field.help_text %}
                            <div class="form-help">{{ field.help_text }}</div>
                        {% endif %}
                        {% if field.errors %}
                            <div class="form-errors">{{ field.errors }}</div>
                        {% endif %}
                    </div>
                {% endfor %}

                <button type="submit" class="btn btn-primary" style="width: 100%;">Register</button>

                <div style="margin-top: 1rem; text-align: center;">
                    Already have an account? <a href="{% url 'login' %}">Login</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''
        (templates_dir / "register.html").write_text(register_template)

        # Profile template
        profile_template = '''{% extends "base.html" %}

{% block title %}Profile{% endblock %}

{% block content %}
<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>My Profile</h2>
        </div>
        <div class="card-body">
            <p><strong>Name:</strong> {{ user.get_full_name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Joined:</strong> {{ user.date_joined|date:"F d, Y" }}</p>

            <div style="margin-top: 2rem;">
                <a href="{% url 'password_change' %}" class="btn btn-outline">Change Password</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        (templates_dir / "profile.html").write_text(profile_template)

    def _generate_api_auth(self, accounts_dir: Path):
        """Generate API authentication (serializers, JWT views)."""
        # Create serializers.py
        serializers_content = '''"""
API serializers for authentication.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
'''
        (accounts_dir / "serializers.py").write_text(serializers_content)

        # Create api_views.py
        api_views_content = '''"""
API views for authentication.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserRegistrationSerializer

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class CurrentUserAPIView(generics.RetrieveAPIView):
    """API endpoint for current user info."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
'''
        (accounts_dir / "api_views.py").write_text(api_views_content)

    def _generate_auth_urls(self, accounts_dir: Path):
        """Generate URL configuration for accounts app."""
        auth_type = self.answers.get('auth_type', 'hybrid')

        urls_content = '''"""
URL configuration for accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views

'''

        if auth_type in ['web', 'hybrid']:
            urls_content += "from . import views\n"

        if auth_type in ['api', 'hybrid']:
            urls_content += "from . import api_views\n"
            urls_content += "from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView\n"

        urls_content += "\n\nurlpatterns = [\n"

        # Web URLs
        if auth_type in ['web', 'hybrid']:
            urls_content += '''    # Web Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
'''

        # API URLs
        if auth_type in ['api', 'hybrid']:
            urls_content += '''
    # API Authentication
    path('api/auth/register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('api/auth/me/', api_views.CurrentUserAPIView.as_view(), name='api_current_user'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
'''

        urls_content += "]\n"

        (accounts_dir / "urls.py").write_text(urls_content)

    def create_django_project(self):
        """Create initial Django project files."""
        print("\n🏗️  Creating Django project files...")

        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Create requirements files
        base_requirements = """Django>=5.0,<5.1
psycopg2-binary>=2.9.5
python-decouple>=3.8
Pillow>=10.0.0
whitenoise>=6.6.0
gunicorn[gevent]>=21.2.0

# Modern tooling
structlog>=24.1.0
django-health-check>=3.18.0
httpx>=0.27.0
"""
        
        if self.answers['use_redis']:
            base_requirements += "redis>=5.0.0\ndjango-redis>=5.4.0\n"
        
        if self.answers['use_celery']:
            base_requirements += "celery>=5.3.0\n"

        # Auth-related packages (if auth is included)
        if self.answers.get('include_auth', True):
            base_requirements += "\n# Authentication & API\n"
            base_requirements += "djangorestframework>=3.14.0\n"
            base_requirements += "djangorestframework-simplejwt>=5.3.0\n"
            base_requirements += "django-cors-headers>=4.3.0\n"
            if self.answers.get('use_api'):
                base_requirements += "drf-spectacular>=0.27.0\n"
            if self.answers.get('enable_2fa'):
                base_requirements += "django-otp>=1.3.0\nqrcode>=7.4.2\n"
        elif self.answers.get('use_api'):
            # API without auth system
            base_requirements += "djangorestframework>=3.14.0\ndrf-spectacular>=0.27.0\n"

        if self.answers['use_sentry']:
            base_requirements += "\n# Monitoring\nsentry-sdk>=1.39.0\n"
        
        (self.project_dir / "requirements" / "base.txt").write_text(base_requirements)
        
        dev_requirements = """-r base.txt
# Development & debugging
django-debug-toolbar>=4.2.0
django-extensions>=3.2.0
django-browser-reload>=1.12.0

# Code quality (modern tooling)
ruff>=0.6.0
mypy>=1.11.0
django-stubs>=5.0.0
bandit>=1.7.9
django-migration-linter>=5.1.0

# Template formatting (Django-aware HTML formatter)
djhtml>=3.0.6

# Testing
pytest>=7.4.0
pytest-django>=4.7.0
pytest-cov>=4.1.0
pytest-xdist>=3.6.0
factory-boy>=3.3.0
faker>=30.0.0

# Pre-commit hooks
pre-commit>=3.8.0
"""
        
        (self.project_dir / "requirements" / "development.txt").write_text(dev_requirements)
        (self.project_dir / "requirements" / "production.txt").write_text("-r base.txt\n")
        
        # Create .env.example
        env_example = f"""# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME={self.answers['project_name_snake']}_db
DB_USER={self.answers['project_name_snake']}_user
DB_PASSWORD=secure-password-here
DB_HOST=db
DB_PORT=5432
"""
        
        if self.answers['use_redis']:
            env_example += "\n# Redis\nREDIS_URL=redis://redis:6379/0\n"
            
        if self.answers['use_sentry']:
            env_example += "\n# Sentry\nSENTRY_DSN=your-sentry-dsn-here\n"
            
        if self.answers.get('use_cloudflare'):
            env_example += f"""
# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=your-tunnel-token-here
DOMAIN_NAME={self.answers.get('domain_name', 'example.com')}
"""
        
        (self.project_dir / ".env.example").write_text(env_example)
        
        # Create .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.env.*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
backups/
*.sql
cloudflared/*.json
cloudflared/*.pem
"""
        
        (self.project_dir / ".gitignore").write_text(gitignore)
        
        # Create .python-version for pyenv auto-activation
        (self.project_dir / ".python-version").write_text(self.answers['project_name'])
        
        # Create docker-compose.yml from template
        self._process_docker_template(
            script_dir / "templates" / "docker" / "docker-compose.yml.template",
            self.project_dir / "docker-compose.yml"
        )

        # Create Dockerfile from template
        self._process_docker_template(
            script_dir / "templates" / "docker" / "Dockerfile.template",
            self.project_dir / "Dockerfile"
        )

        # Create enhanced docker-entrypoint.sh
        self._process_docker_template(
            script_dir / "templates" / "docker" / "docker-entrypoint.sh.template",
            self.project_dir / "docker-entrypoint.sh"
        )
        os.chmod(self.project_dir / "docker-entrypoint.sh", 0o755)
        
        # Setup Cloudflare if requested
        if self.answers.get('use_cloudflare'):
            self._setup_cloudflare_tunnel(script_dir)

        # Create initial README from template
        readme_template = (script_dir / "templates" / "README.md").read_text()
        readme_content = readme_template.replace(
            '{project_name_title}', self.answers['project_name'].title().replace('-', ' ')
        ).replace(
            '{project_description}', self.answers['project_description']
        )
        (self.project_dir / "README.md").write_text(readme_content)
        
        print("✅ Django project files created")
    
    def _process_docker_template(self, source: Path, destination: Path):
        """Process Docker template files with placeholder replacement."""
        if not source.exists():
            print(f"⚠️  Warning: Template {source.name} not found, skipping...")
            return

        content = source.read_text()

        # Extract major.minor version (e.g., "3.13" from "3.13.1")
        python_version = self.answers['python_version']
        python_major_minor = '.'.join(python_version.split('.')[:2])

        # Replace placeholders
        replacements = {
            "{{PROJECT_NAME}}": self.answers['project_name'],
            "{{PYTHON_VERSION}}": python_version,
            "{{PYTHON_MAJOR_MINOR}}": python_major_minor,
            "{{DOMAIN_NAME}}": self.answers.get('domain_name', 'example.com'),
            "{{TUNNEL_ID}}": "your-tunnel-id-here",
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # Remove optional services if not needed
        if not self.answers.get('use_redis', True):
            content = self._remove_docker_service(content, 'redis')
        if not self.answers.get('use_celery', False):
            content = self._remove_docker_service(content, 'celery')
            content = self._remove_docker_service(content, 'celery-beat')
        if not self.answers.get('use_cloudflare', False):
            content = self._remove_docker_service(content, 'cloudflared')
        
        destination.write_text(content)
    
    def _remove_docker_service(self, content: str, service_name: str) -> str:
        """Remove a service section from docker-compose.yml content."""
        lines = content.split('\n')
        result_lines = []
        skip_service = False
        service_indent = 0
        
        for line in lines:
            # Check if this is the start of the service to remove
            if line.strip().startswith(f'{service_name}:'):
                skip_service = True
                service_indent = len(line) - len(line.lstrip())
                continue
            
            if skip_service:
                # Check if we've reached the next service or section
                current_indent = len(line) - len(line.lstrip()) if line.strip() else float('inf')
                if line.strip() and current_indent <= service_indent:
                    skip_service = False
                    result_lines.append(line)
                # Skip lines that are part of the service
                continue
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _setup_cloudflare_tunnel(self, script_dir: Path):
        """Set up Cloudflare tunnel configuration."""
        print("🌐 Setting up Cloudflare Tunnel...")
        
        # Create cloudflared directory
        cloudflared_dir = self.project_dir / "cloudflared"
        cloudflared_dir.mkdir(exist_ok=True)
        
        # Copy and process config template
        config_template = script_dir / "templates" / "config" / "cloudflared-config.yml.template"
        if config_template.exists():
            self._process_template(
                config_template,
                cloudflared_dir / "config.yml",
                {
                    "{{TUNNEL_ID}}": "your-tunnel-id-here",
                    "{{DOMAIN_NAME}}": self.answers.get('domain_name', 'example.com'),
                }
            )
        
        # Create README for Cloudflare setup
        cloudflare_readme = f"""# Cloudflare Tunnel Setup

## Steps to configure your tunnel:

1. **Create tunnel in Cloudflare dashboard**:
   ```bash
   cloudflared tunnel create {self.answers['project_name']}
   ```

2. **Copy tunnel credentials**:
   - Download the .json credentials file
   - Place it in this directory as `<tunnel-id>.json`

3. **Update configuration**:
   - Edit `config.yml` and replace `your-tunnel-id-here` with your actual tunnel ID
   - Verify domain name is correct: `{self.answers.get('domain_name', 'example.com')}`

4. **Configure DNS**:
   - In Cloudflare dashboard, add CNAME record:
   - Name: `{self.answers.get('domain_name', 'example.com').split('.')[0]}`
   - Target: `<tunnel-id>.cfargotunnel.com`

5. **Add tunnel token to .env**:
   ```
   CLOUDFLARE_TUNNEL_TOKEN=your-tunnel-token-here
   ```

6. **Test the tunnel**:
   ```bash
   docker-compose up cloudflared
   ```

## Security Notes:
- Keep the .json credentials file secure and never commit it to git
- The tunnel provides secure access without opening firewall ports
- SSL/TLS termination is handled by Cloudflare
"""
        
        (cloudflared_dir / "README.md").write_text(cloudflare_readme)
        
        # Add to .gitignore
        gitignore_additions = """
# Cloudflare Tunnel
cloudflared/*.json
cloudflared/*.pem
"""
        
        gitignore_path = self.project_dir / ".gitignore"
        if gitignore_path.exists():
            current_gitignore = gitignore_path.read_text()
            if "cloudflared/*.json" not in current_gitignore:
                gitignore_path.write_text(current_gitignore + gitignore_additions)
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml content."""
        services = f"""version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - ./.env
    environment:
      POSTGRES_DB: ${{DB_NAME}}
      POSTGRES_USER: ${{DB_USER}}
      POSTGRES_PASSWORD: ${{DB_PASSWORD}}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d ${{DB_NAME}} -U ${{DB_USER}}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: ./
    restart: always
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
"""
        
        if self.answers['use_redis']:
            services += """      - redis
"""
            
        services += """    env_file:
      - ./.env
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production

  nginx:
    build: ./nginx
    restart: always
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    ports:
      - "80:80"
"""

        if self.answers['use_redis']:
            services += """
  redis:
    image: redis:7-alpine
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
"""
            
        if self.answers['use_celery']:
            services += f"""
  celery:
    build: ./
    command: celery -A config worker -l info
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - ./.env
    depends_on:
      - db
      - redis

  celery-beat:
    build: ./
    command: celery -A config beat -l info
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - ./.env
    depends_on:
      - db
      - redis
"""

        services += """
volumes:
  postgres_data:
  static_volume:
  media_volume:
"""
        
        return services
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile content."""
        return f"""FROM python:{self.answers['python_version']}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    postgresql-client \\
    gcc \\
    python3-dev \\
    musl-dev \\
    libpq-dev \\
    netcat-traditional \\
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app
RUN mkdir -p /app/staticfiles /app/media

# Install Python dependencies
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip && pip install -r requirements/production.txt

# Copy project files
COPY --chown=app:app . /app/

# Copy and set entrypoint
COPY --chown=app:app ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Change to app user
USER app

ENTRYPOINT ["/docker-entrypoint.sh"]
"""
    
    def _show_documentation_summary(self):
        """Display comprehensive summary of all documentation files."""
        print("\n" + "=" * 50)
        print("📚 DOCUMENTATION GUIDE")
        print("=" * 50)
        print("\nAll documentation files are located in your project's docs/ folder.")
        print("These files provide comprehensive guidance for development:\n")

        docs = [
            {
                "file": "CLAUDE.md",
                "location": "Root directory",
                "purpose": "AI Assistant Memory & Project Context",
                "description": "Living document that tracks project decisions, architecture, and context. Update this as your project evolves. Essential for AI assistants to understand your project.",
                "use_when": "Working with AI assistants, onboarding developers, documenting decisions"
            },
            {
                "file": "README.md",
                "location": "Root directory",
                "purpose": "Project Overview & Quick Start",
                "description": "First thing visitors see. Contains project description, quick start commands, and links to detailed documentation.",
                "use_when": "Sharing project on GitHub, providing quick reference"
            },
            {
                "file": "PROJECT_SETUP_SUMMARY.md",
                "location": "Root directory",
                "purpose": "Setup Configuration Summary",
                "description": "Complete record of all choices made during setup (colors, features, architecture). Reference for AI assistants and new developers.",
                "use_when": "Refreshing memory on setup decisions, onboarding team members"
            },
            {
                "file": "docs/SETUP_GUIDE.md",
                "location": "docs/",
                "purpose": "Complete Setup Instructions",
                "description": "Step-by-step guide for setting up development environment, installing dependencies, configuring Django, and deploying to production.",
                "use_when": "Initial setup, deploying to new server, troubleshooting environment"
            },
            {
                "file": "docs/BEGINNERS_GUIDE.md",
                "location": "docs/",
                "purpose": "Complete Beginner's Tutorial",
                "description": "Comprehensive guide for developers new to Django or this template. Covers concepts, project structure, and common tasks with examples.",
                "use_when": "Learning Django, understanding project structure, first-time contributors"
            },
            {
                "file": "docs/STYLE_GUIDE.md",
                "location": "docs/",
                "purpose": "Design System & CSS Guidelines",
                "description": f"Your custom design system with colors ({self.answers['primary_color']}), spacing, typography, and component patterns. CSS architecture and naming conventions.",
                "use_when": "Creating UI components, styling pages, maintaining design consistency"
            },
            {
                "file": "docs/CODING_GUIDE.md",
                "location": "docs/",
                "purpose": "Code Standards & Best Practices",
                "description": "Python and Django coding standards, naming conventions, testing practices, and code organization patterns specific to this project.",
                "use_when": "Writing new code, code reviews, resolving style debates"
            },
            {
                "file": "docs/FILE_HANDLING.md",
                "location": "docs/",
                "purpose": "File Upload & Storage Guide",
                "description": "Complete guide for handling user uploads, bulk imports, image processing, security validation, and cloud storage integration.",
                "use_when": "Implementing file uploads, adding image handling, bulk data import"
            },
            {
                "file": "docs/AUTH_SETUP.md",
                "location": "docs/",
                "purpose": "Authentication Setup & User Management",
                "description": f"Complete guide for authentication system: creating superuser, password requirements, login/register, JWT API tokens, and troubleshooting. {'Includes 2FA setup.' if self.answers.get('enable_2fa') else ''}",
                "use_when": "Setting up authentication, creating users, troubleshooting login issues"
            } if self.answers.get('include_auth', True) else None,
            {
                "file": "docs/PWA_SETUP.md",
                "location": "docs/",
                "purpose": "PWA & Open Graph Configuration",
                "description": "Instructions for implementing Progressive Web App features and social media sharing tags. Includes ready-to-use HTML snippets.",
                "use_when": "Making app installable, optimizing social shares, adding offline support"
            },
        ]

        # Filter out None entries
        docs = [d for d in docs if d is not None]

        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc['file']}")
            print(f"   📍 Location: {doc['location']}")
            print(f"   🎯 {doc['purpose']}")
            print(f"   📖 {doc['description']}")
            print(f"   💡 Use when: {doc['use_when']}")
            print()

        print("=" * 50)
        print("💡 QUICK REFERENCE")
        print("=" * 50)
        auth_line = "- Create users, troubleshoot login  → docs/AUTH_SETUP.md\n" if self.answers.get('include_auth', True) else ""

        print(f"""
Need to...                          Open this file:
- Understand project architecture   → CLAUDE.md
- Set up development environment    → docs/SETUP_GUIDE.md
- Learn Django basics for project   → docs/BEGINNERS_GUIDE.md
- Style a component                 → docs/STYLE_GUIDE.md
- Add file uploads                  → docs/FILE_HANDLING.md
{auth_line}- Configure social sharing          → docs/PWA_SETUP.md
- Follow code standards             → docs/CODING_GUIDE.md
- Review setup choices              → PROJECT_SETUP_SUMMARY.md
""")

    def show_next_steps(self):
        """Show simplified next steps after setup."""
        print("\n" + "=" * 50)
        print("✅ Project Setup Complete!")
        print("=" * 50)

        print(f"\n📁 Project created in: {self.project_dir}")
        print(f"📋 Template factory kept at: {Path(__file__).parent}")
        print("\n💡 The BuildTemplate folder stays intact for creating more projects!")

        print("\n" + "=" * 50)
        print("🚀 Continue Your Setup")
        print("=" * 50)

        print(f"""
📍 Next Steps:

1. Navigate to your new project:
   cd {self.project_dir}

2. Choose your path:

   🤖 AUTOMATED (Recommended):
   python3 continue_here.py

   📖 MANUAL:
   Open and follow: NEXT_STEPS.md

The continuation script will:
  ✓ Create Python environment
  ✓ Install dependencies
  ✓ Set up Django
  ✓ Initialize git repository
  ✓ Run migrations

📚 All detailed documentation is in the docs/ folder.
🎨 Your theme colors: {self.answers['primary_color']}, {self.answers['secondary_color']}, {self.answers['accent_color']}

Happy coding! 🎉
""")
    
    def generate_summary_file(self):
        """Generate a comprehensive project summary for AI assistants."""
        print("\n📝 Generating project summary...")

        # Get the directory where this script is located
        script_dir = Path(__file__).parent

        # Read template
        template_path = script_dir / "templates" / "PROJECT_SETUP_SUMMARY.md"
        summary_template = template_path.read_text()

        # Build features list
        features = []
        features.append(f"- {'✅' if self.answers['use_celery'] else '❌'} Celery (Background Tasks)")
        features.append(f"- {'✅' if self.answers['use_redis'] else '❌'} Redis (Caching)")
        features.append(f"- {'✅' if self.answers['use_api'] else '❌'} REST API")
        features.append(f"- {'✅' if self.answers['use_sentry'] else '❌'} Sentry Error Tracking")

        # Build remote server info
        remote_server_info = ""
        if self.answers.get('remote_server'):
            remote_server_info = f"- Server: {self.answers.get('remote_server', 'N/A')}\n"
            remote_server_info += f"- Directory: {self.answers.get('remote_backup_dir', 'N/A')}"

        # Replace placeholders
        replacements = {
            '{project_name_upper}': self.answers['project_name'].upper(),
            '{generated_date}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{project_name}': self.answers['project_name'],
            '{project_description}': self.answers['project_description'],
            '{domain}': self.answers['domain'],
            '{target_users}': self.answers['target_users'],
            '{python_version}': self.answers['python_version'],
            '{primary_color}': self.answers['primary_color'],
            '{secondary_color}': self.answers['secondary_color'],
            '{accent_color}': self.answers['accent_color'],
            '{design_style}': self.answers['design_style'].title(),
            '{border_radius}': self.answers['border_radius'],
            '{shadow_style}': self.answers['shadow_style'].title(),
            '{dark_mode}': 'Enabled' if self.answers['dark_mode'] else 'Disabled',
            '{mobile_nav}': self.answers['mobile_nav'].replace('-', ' ').title(),
            '{share_image}': 'Provided ✓' if self.answers.get('share_image_path') else 'Not provided - add later',
            '{dev_database}': self.answers['dev_database'].upper(),
            '{features_list}': '\n'.join(features),
            '{remote_backup}': 'Configured' if self.answers.get('remote_server') else 'Not configured',
            '{remote_server_info}': remote_server_info,
            '{compliance_reqs}': self.answers.get('compliance_reqs', 'Standard web application requirements'),
            '{special_features}': self.answers.get('special_features', 'Standard Django features'),
        }

        summary_content = summary_template
        for placeholder, value in replacements.items():
            summary_content = summary_content.replace(placeholder, value)

        # Write summary file
        (self.project_dir / "PROJECT_SETUP_SUMMARY.md").write_text(summary_content)
        print("✅ Project summary generated: PROJECT_SETUP_SUMMARY.md")

        # Generate URL configuration reminder
        self.generate_url_setup_reminder()

    def generate_url_setup_reminder(self):
        """Generate a reminder file for URLs that need to be manually added."""
        url_reminder = f"""# ⚠️ IMPORTANT: URL Configuration Required

After running `django-admin startproject config .`, you need to add these URLs to `config/urls.py`:

## Required URLs

Add these imports and URL patterns to your `config/urls.py` file:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check endpoints (for Docker, k8s, monitoring)
    path('health/', include('health_check.urls')),

    # Your app URLs
    # path('', include('apps.core.urls')),  # Add your app URLs here
]

# Development-only URLs
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        # Django Debug Toolbar
        path('__debug__/', include(debug_toolbar.urls)),

        # Browser auto-reload (saves you from manual refreshes!)
        path('__reload__/', include('django_browser_reload.urls')),
    ]

    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Why These URLs?

1. **`/health/`** - Health check endpoint for:
   - Docker health checks
   - Kubernetes liveness/readiness probes
   - Uptime monitoring services
   - Load balancer health checks

2. **`/__reload__/`** - Browser auto-reload:
   - Automatically refreshes your browser when you save code
   - HUGE productivity boost during development
   - Only enabled in DEBUG mode

3. **`/__debug__/`** - Django Debug Toolbar:
   - Shows SQL queries, performance metrics
   - Only enabled in DEBUG mode

## Testing Health Checks

After adding the URLs and starting your server:

```bash
# Start development server
make run

# In another terminal, test health endpoint
make health
# or
curl http://localhost:8000/health/
```

## Delete This File

Once you've added these URLs to `config/urls.py`, you can delete this reminder file!

---

**📝 Note**: These URLs are documented in:
- `CLAUDE.md` - AI assistant reference
- `docs/SETUP_GUIDE.md` - Complete setup documentation
"""

        (self.project_dir / "CONFIGURE_URLS.md").write_text(url_reminder)
        print("📋 URL configuration reminder created: CONFIGURE_URLS.md")

    def generate_continue_files(self):
        """Generate continue_here.py and NEXT_STEPS.md in the new project."""
        print("\n📝 Generating continuation files...")

        # Get the directory where this script is located (BuildTemplate)
        template_dir = Path(__file__).parent / "templates"

        # Read templates
        next_steps_template = (template_dir / "NEXT_STEPS.md").read_text()
        continue_py_template = (template_dir / "continue_here.py").read_text()

        # Replace placeholders
        replacements = {
            '{project_name}': self.answers['project_name'],
            '{python_version}': self.answers['python_version'],
            '{primary_color}': self.answers['primary_color'],
            '{secondary_color}': self.answers['secondary_color'],
            '{accent_color}': self.answers['accent_color'],
            '{design_style}': self.answers['design_style'],
        }

        for placeholder, value in replacements.items():
            next_steps_template = next_steps_template.replace(placeholder, value)
            continue_py_template = continue_py_template.replace(placeholder, value)

        # Write files to new project directory
        (self.project_dir / "NEXT_STEPS.md").write_text(next_steps_template)
        (self.project_dir / "continue_here.py").write_text(continue_py_template)

        # Make Python script executable
        import stat
        continue_py_path = self.project_dir / "continue_here.py"
        continue_py_path.chmod(continue_py_path.stat().st_mode | stat.S_IEXEC)

        print("  ✅ Created NEXT_STEPS.md")
        print("  ✅ Created continue_here.py (executable)")

    def offer_open_vscode(self):
        """Offer to open the new project in VSCode."""
        print("\n" + "=" * 50)
        print("🎉 Opening Your Project")
        print("=" * 50)

        if input("\n🚀 Open project in new VSCode window? (Y/n): ").lower() != 'n':
            import subprocess
            try:
                subprocess.run(['code', str(self.project_dir)], check=True)
                print("\n✅ Opening VSCode...")
                print(f"\n📍 Once VSCode opens, you'll be in: {self.project_dir}")
                print("🚀 Run this in the VSCode terminal: python3 continue_here.py")
            except subprocess.CalledProcessError:
                print("\n❌ Could not open VSCode")
                print(f"📂 Manually: cd {self.project_dir}")
                print("🚀 Then run: python3 continue_here.py")
            except FileNotFoundError:
                print("\n⚠️  VSCode 'code' command not found.")
                print("\n📋 To fix this (takes 30 seconds):")
                print("   1. Open VSCode")
                print("   2. Press Cmd + Shift + P")
                print("   3. Type: 'shell command'")
                print("   4. Click: 'Shell Command: Install code command in PATH'")
                print(f"\n📂 For now, manually open: {self.project_dir}")
                print("🚀 Then run: python3 continue_here.py")
        else:
            print(f"\n📂 Next: cd {self.project_dir}")
            print("🚀 Then: python3 continue_here.py")


def main():
    """Main function to run the project setup wizard."""
    setup = ProjectSetup()
    setup.run()


if __name__ == "__main__":
    main()