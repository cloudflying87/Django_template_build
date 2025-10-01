#!/usr/bin/env python3
"""
Interactive Django Project Setup Script
Asks questions and automatically fills in all template documents
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ProjectSetup:
    def __init__(self):
        self.answers = {}
        self.project_dir = None  # Will be set after getting project name
        
    def run(self):
        """Run the complete setup process."""
        print("🚀 Django Project Setup Wizard")
        print("=" * 50)
        print("This wizard will help you set up a new Django project")
        print("with custom styling, build scripts, and documentation.\n")
        
        # Collect all answers
        self.collect_project_info()
        self.collect_style_preferences()
        self.collect_technical_choices()
        self.collect_domain_specific()
        
        # Show summary
        self.show_summary()
        
        # Confirm and create
        if self.confirm_setup():
            self.create_project_structure()
            self.fill_templates()
            self.generate_css()
            self.create_django_project()
            self.generate_summary_file()
            self.show_next_steps()
            self.offer_cleanup()
        else:
            print("\n❌ Setup cancelled.")
    
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
                # Set project directory based on project name
                self.project_dir = Path.cwd() / project_name
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
    
    def collect_technical_choices(self):
        """Collect technical preferences."""
        print("\n⚙️  Technical Choices")
        print("-" * 30)
        
        # Python version
        default_python = "3.11.8"
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
        return input("Proceed with setup? (Y/n): ").lower() != 'n'
    
    def create_project_structure(self):
        """Create the project directory structure."""
        print("\n📁 Creating project structure...")
        
        directories = [
            "apps/core/templates/core/includes",
            "apps/core/management/commands",
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
            script_dir / "CLAUDE_TEMPLATE.md",
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
        shutil.copy(script_dir / "STYLE_GUIDE_TEMPLATE.md", self.project_dir / "docs" / "STYLE_GUIDE.md")
        shutil.copy(script_dir / "CODING_GUIDE_TEMPLATE.md", self.project_dir / "docs" / "CODING_GUIDE.md")
        shutil.copy(script_dir / "DJANGO_PROJECT_STARTER_GUIDE.md", self.project_dir / "docs" / "SETUP_GUIDE.md")

        # Copy beginner's guide if it exists
        if (script_dir / "COMPLETE_BEGINNERS_GUIDE.md").exists():
            shutil.copy(script_dir / "COMPLETE_BEGINNERS_GUIDE.md", self.project_dir / "docs" / "BEGINNERS_GUIDE.md")
            print("  ✅ Copied beginner's guide")
        
        # Copy nginx configuration
        if (script_dir / "nginx.conf.template").exists():
            shutil.copy(script_dir / "nginx.conf.template", self.project_dir / "nginx" / "nginx.conf")
        if (script_dir / "nginx.Dockerfile.template").exists():
            shutil.copy(script_dir / "nginx.Dockerfile.template", self.project_dir / "nginx" / "Dockerfile")
        
        # Copy Makefile
        if (script_dir / "Makefile.template").exists():
            self._process_template(
                script_dir / "Makefile.template",
                self.project_dir / "Makefile",
                {"PROJECT_NAME": self.answers['project_name']}
            )
        
        # Copy pre-commit config (new ruff-based version)
        if (script_dir / ".pre-commit-config.yaml.template").exists():
            shutil.copy(script_dir / ".pre-commit-config.yaml.template", self.project_dir / ".pre-commit-config.yaml")

        # Copy pyproject.toml for tool configuration
        if (script_dir / "pyproject.toml.template").exists():
            shutil.copy(script_dir / "pyproject.toml.template", self.project_dir / "pyproject.toml")

        # Copy GitHub workflows
        workflows_dir = self.project_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        for workflow_file in ["ci.yml.template", "dependency-review.yml.template", "codeql.yml.template"]:
            workflow_path = script_dir / ".github" / "workflows" / workflow_file
            if workflow_path.exists():
                output_name = workflow_file.replace(".template", "")
                shutil.copy(workflow_path, workflows_dir / output_name)
                # Replace PROJECT_NAME placeholder
                workflow_content = (workflows_dir / output_name).read_text()
                workflow_content = workflow_content.replace("{{PROJECT_NAME}}", self.answers['project_name'])
                (workflows_dir / output_name).write_text(workflow_content)
        
        # Create Django settings templates
        self._create_django_settings(script_dir)
        
        # Copy validation script
        if (script_dir / "validate_setup.py").exists():
            shutil.copy(script_dir / "validate_setup.py", self.project_dir / "validate_setup.py")
            os.chmod(self.project_dir / "validate_setup.py", 0o755)
        
        # Update STYLE_GUIDE.md with answers
        self._fill_style_guide()
        
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
            template_path = script_dir / template_name
            if template_path.exists():
                self._process_template(
                    template_path,
                    settings_dir / output_name,
                    replacements
                )
                print(f"  ✅ Created {output_name}")
            else:
                print(f"  ⚠️  Template {template_name} not found")
    
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
    
    def create_django_project(self):
        """Create initial Django project files."""
        print("\n🏗️  Creating Django project files...")
        
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Initialize git repository
        print("\n🔧 Initializing git repository...")
        os.system("git init")
        os.system("git branch -M main")  # Use 'main' as default branch
        
        # Create requirements files
        base_requirements = """Django>=5.0,<5.1
psycopg2-binary>=2.9.5
python-decouple>=3.8
Pillow>=10.0.0
whitenoise>=6.6.0
gunicorn[gevent]>=21.2.0
"""
        
        if self.answers['use_redis']:
            base_requirements += "redis>=5.0.0\ndjango-redis>=5.4.0\n"
        
        if self.answers['use_celery']:
            base_requirements += "celery>=5.3.0\n"
            
        if self.answers['use_api']:
            base_requirements += "djangorestframework>=3.14.0\ndrf-spectacular>=0.27.0\n"
            
        if self.answers['use_sentry']:
            base_requirements += "sentry-sdk>=1.39.0\n"
        
        (self.project_dir / "requirements" / "base.txt").write_text(base_requirements)
        
        dev_requirements = """-r base.txt
# Development & debugging
django-debug-toolbar>=4.2.0
django-extensions>=3.2.0

# Code quality (modern tooling)
ruff>=0.6.0
mypy>=1.11.0
django-stubs>=5.0.0
bandit>=1.7.9

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
            script_dir / "docker-compose.yml.template",
            self.project_dir / "docker-compose.yml"
        )
        
        # Create Dockerfile from template
        self._process_docker_template(
            script_dir / "Dockerfile.template",
            self.project_dir / "Dockerfile"
        )
        
        # Create enhanced docker-entrypoint.sh
        self._process_docker_template(
            script_dir / "docker-entrypoint.sh.template",
            self.project_dir / "docker-entrypoint.sh"
        )
        os.chmod(self.project_dir / "docker-entrypoint.sh", 0o755)
        
        # Setup Cloudflare if requested
        if self.answers.get('use_cloudflare'):
            self._setup_cloudflare_tunnel(script_dir)
        
        # Create initial README
        readme_content = f"""# {self.answers['project_name'].title().replace('-', ' ')}

{self.answers['project_description']}

## Quick Start

See `docs/SETUP_GUIDE.md` for complete setup instructions.

```bash
# Development
make run

# Production
make deploy
```

## Documentation

- Project Overview: `CLAUDE.md`
- Setup Guide: `docs/SETUP_GUIDE.md`
- Style Guide: `docs/STYLE_GUIDE.md`
- Coding Standards: `docs/CODING_GUIDE.md`
"""
        (self.project_dir / "README.md").write_text(readme_content)
        
        print("✅ Django project files created")
    
    def _process_docker_template(self, source: Path, destination: Path):
        """Process Docker template files with placeholder replacement."""
        if not source.exists():
            print(f"⚠️  Warning: Template {source.name} not found, skipping...")
            return
            
        content = source.read_text()
        
        # Replace placeholders
        replacements = {
            "{{PROJECT_NAME}}": self.answers['project_name'],
            "{{PYTHON_VERSION}}": self.answers['python_version'],
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
        config_template = script_dir / "cloudflared-config.yml.template"
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
COPY requirements/production.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY --chown=app:app . /app/

# Copy and set entrypoint
COPY --chown=app:app ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Change to app user
USER app

ENTRYPOINT ["/docker-entrypoint.sh"]
"""
    
    def show_next_steps(self):
        """Show next steps after setup."""
        print("\n" + "=" * 50)
        print("✅ Project Setup Complete!")
        print("=" * 50)
        
        print(f"\n📁 Project created in: {self.project_dir}")
        
        print("\n🚀 Next Steps:")
        print(f"""
1. Create Python environment (auto-activates with .python-version):
   pyenv virtualenv {self.answers['python_version']} {self.answers['project_name']}
   cd . # Re-enter directory to activate environment

2. Install UV for blazing-fast dependency management (optional but recommended):
   pip install uv
   # UV is 10-100x faster than pip!

3. Install dependencies:
   make install-uv  # Install uv package manager
   make install     # Install all dependencies (will use uv if available)

4. Setup Django project:
   django-admin startproject config .
   python manage.py startapp core
   mv core apps/

5. Configure Django settings:
   - Move settings.py to config/settings/base.py
   - Create development.py and production.py
   - Update INSTALLED_APPS to include 'apps.core'

6. Initial setup (runs migrations, installs pre-commit hooks):
   make setup  # One command does it all!

7. Start development:
   make run  # Equivalent to python manage.py runserver

8. Code quality automation:
   make format      # Auto-format with ruff
   make lint        # Check code quality
   make type-check  # Type checking with mypy
   make security    # Security scan with bandit
   make quality     # Run all checks

9. Initialize git and push:
   git add .
   git commit -m "Initial project setup"
   git remote add origin git@github.com:username/{self.answers['project_name']}.git
   git push -u origin main

10. Enable GitHub Actions:
    - CI workflow runs automatically on push/PR
    - CodeQL security scanning
    - Dependency review on PRs

11. Production deployment:
    make deploy  # Uses build.sh script with backup

12. Validate setup:
    python validate_setup.py  # Verify everything works
""")
        
        print("\n📚 Documentation:")
        print("  - Project overview: CLAUDE.md")
        print("  - Complete beginner's guide: docs/BEGINNERS_GUIDE.md")
        print("  - Style guide: docs/STYLE_GUIDE.md")
        print("  - Coding standards: docs/CODING_GUIDE.md")
        print("  - Setup instructions: docs/SETUP_GUIDE.md")
        
        print("\n🎨 Theme:")
        print(f"  - Primary: {self.answers['primary_color']}")
        print(f"  - Secondary: {self.answers['secondary_color']}")
        print(f"  - CSS generated in: static/css/base.css")
        
        print("\nHappy coding! 🎉")
    
    def generate_summary_file(self):
        """Generate a comprehensive project summary for AI assistants."""
        print("\n📝 Generating project summary...")
        
        summary_content = f"""# {self.answers['project_name'].upper()} - Project Setup Summary

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Project Overview

**Name**: {self.answers['project_name']}  
**Description**: {self.answers['project_description']}  
**Domain**: {self.answers['domain']}  
**Target Users**: {self.answers['target_users']}  
**Python Version**: {self.answers['python_version']}

## 🎨 Design & Theme

**Primary Color**: {self.answers['primary_color']}  
**Secondary Color**: {self.answers['secondary_color']}  
**Accent Color**: {self.answers['accent_color']}  
**Design Style**: {self.answers['design_style'].title()}  
**Border Radius**: {self.answers['border_radius']}  
**Shadow Style**: {self.answers['shadow_style'].title()}  
**Dark Mode**: {'Enabled' if self.answers['dark_mode'] else 'Disabled'}  
**Mobile Navigation**: {self.answers['mobile_nav'].replace('-', ' ').title()}

## ⚙️ Technical Configuration

**Development Database**: {self.answers['dev_database'].upper()}  
**Features Enabled**:
{f"- ✅ Celery (Background Tasks)" if self.answers['use_celery'] else "- ❌ Celery"}
{f"- ✅ Redis (Caching)" if self.answers['use_redis'] else "- ❌ Redis"}
{f"- ✅ REST API" if self.answers['use_api'] else "- ❌ REST API"}
{f"- ✅ Sentry (Error Tracking)" if self.answers['use_sentry'] else "- ❌ Sentry Error Tracking"}

**Remote Backup**: {'Configured' if self.answers.get('remote_server') else 'Not configured'}
{f"- Server: {self.answers.get('remote_server', 'N/A')}" if self.answers.get('remote_server') else ""}
{f"- Directory: {self.answers.get('remote_backup_dir', 'N/A')}" if self.answers.get('remote_backup_dir') else ""}

## 🏗️ Architecture Details

**Development Workflow**:
- Local development with pyenv (no Docker)
- Hot reload with `python manage.py runserver`
- {self.answers['dev_database'].upper()} database for development

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
{self.answers['project_name']}/
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
├── static/css/                  # Custom CSS framework
│   ├── base.css                # Generated theme with your colors
│   └── components/             # Reusable components (buttons, forms, etc.)
├── templates/                   # Django templates
├── docs/                       # Comprehensive documentation
│   ├── SETUP_GUIDE.md         # Complete setup instructions
│   ├── STYLE_GUIDE.md         # Custom styling guidelines
│   └── CODING_GUIDE.md        # Development standards
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

**Industry**: {self.answers['domain']}  
**Compliance Requirements**: {self.answers.get('compliance_reqs', 'Standard web application requirements')}  
**Special Features**: {self.answers.get('special_features', 'Standard Django features')}

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
3. **Use the custom CSS variables** - Primary: {self.answers['primary_color']}, etc.
4. **Follow the build.sh pattern** - Production deployment via Docker
5. **Reference CLAUDE.md** - Contains living project context
6. **Domain focus**: This is a {self.answers['domain']} application for {self.answers['target_users']}

## 🔧 Quick Context for Development

**Current Status**: Fresh project setup completed  
**Ready for**: Django project creation and initial model development  
**Architecture**: Same proven patterns as Keep-Logging project  
**Styling**: Custom {self.answers['design_style']} theme with {self.answers['primary_color']} primary color  
**Deployment**: Docker production, pyenv development

---

*This summary provides complete context for AI assistants and developers joining the project.*
"""
        
        # Write summary file
        (self.project_dir / "PROJECT_SETUP_SUMMARY.md").write_text(summary_content)
        print("✅ Project summary generated: PROJECT_SETUP_SUMMARY.md")
    
    def offer_cleanup(self):
        """Offer to clean up setup files after project is established."""
        print("\n" + "=" * 50)
        print("🧹 Cleanup Options")
        print("=" * 50)
        print("\nYour new project has been created!")
        print(f"📁 Project location: {self.project_dir}")
        print("\nThe template files in the CURRENT directory can be removed.")
        print("\n⚠️  WARNING: This will delete template files from where you ran this script.")
        print("   Make sure you don't need them for other projects!")

        print("\nFiles that will be removed:")
        print("  - setup_new_project.py")
        print("  - All *_TEMPLATE.md files")
        print("  - All *.template files")
        print("  - Documentation (START_HERE.md, guides)")

        print("\nYour NEW PROJECT will keep:")
        print("  - All generated files (CLAUDE.md, build.sh, etc.)")
        print("  - All documentation (in docs/ directory)")
        print("  - PROJECT_SETUP_SUMMARY.md")

        if input("\nRun cleanup now? (y/N): ").lower() == 'y':
            self.run_cleanup()
        else:
            print(f"\n💡 To cleanup later from {Path(__file__).parent}:")
            print("   python setup_new_project.py --cleanup")
    
    def run_cleanup(self):
        """Clean up setup files after project is created."""
        print("\n🧹 Cleaning up template files...")

        # Clean up from the CURRENT directory (where script is located)
        # not from the project directory that was created
        script_dir = Path(__file__).parent

        files_to_remove = [
            "setup_new_project.py",
            "DJANGO_PROJECT_STARTER_GUIDE.md",
            "build_template.sh",
            "STYLE_GUIDE_TEMPLATE.md",
            "CODING_GUIDE_TEMPLATE.md",
            "CLAUDE_TEMPLATE.md",
            "nginx.conf.template",
            "nginx.Dockerfile.template",
            "Makefile.template",
            ".pre-commit-config.yaml.template",
            "pyproject.toml.template",
            "manifest.json.template",
            "service-worker.js.template",
            "Dockerfile.template",
            "docker-compose.yml.template",
            "docker-entrypoint.sh.template",
            "cloudflared-config.yml.template",
            "django-settings-base.py.template",
            "django-settings-development.py.template",
            "django-settings-production.py.template",
            "validate_setup.py",
            "START_HERE.md",
            "COMPLETE_BEGINNERS_GUIDE.md",
            "IMPROVEMENTS_SUMMARY.md",
            "MODERN_TOOLS_GUIDE.md",
            "DJANGO_TEMPLATES_FORMATTING.md",
            "UPGRADE_SUMMARY.md",
            ".github"  # Directory
        ]

        removed_count = 0
        for file_name in files_to_remove:
            file_path = script_dir / file_name
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    removed_count += 1
                    print(f"  ✅ Removed directory {file_name}")
                else:
                    file_path.unlink()
                    removed_count += 1
                    print(f"  ✅ Removed {file_name}")

        if removed_count > 0:
            print(f"\n✅ Cleanup complete! Removed {removed_count} template files.")
            print(f"📁 Your project is ready in: {self.project_dir}")
            print("\n💡 Next: cd into your project and start developing!")
        else:
            print(f"  No template files found to remove in {script_dir}")

        print("\n✨ Template cleanup complete!")


def main():
    """Main function to handle command line arguments."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--cleanup':
        # Run cleanup only
        setup = ProjectSetup()
        setup.run_cleanup()
    else:
        # Run normal setup
        setup = ProjectSetup()
        setup.run()


if __name__ == "__main__":
    main()