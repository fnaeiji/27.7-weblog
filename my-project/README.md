# AI Blog Platform — Persian-First Blog with Editorial Workflow

A Django 5.2 blog application with role-based editorial workflow (Author → Editor → Admin) and a foundation for AI-assisted writing tools.

## Stack

- **Python** 3.12+
- **Django** 5.2 LTS
- **SQLite** (local dev/tests) / PostgreSQL (production)
- **Django Templates** + **Thymeleaf-style** server-rendered UI (RTL, Persian)
- **pytest** + **pytest-django** for testing
- **Ruff** for linting/formatting

## Features (PRD-01 Complete)

- **Public blog**: Homepage + article detail (PUBLISHED only)
- **Markdown → sanitized HTML** (bleach allowlist, XSS-safe)
- **Roles**: `AUTHOR`, `EDITOR`, `ADMIN` (server-side enforcement)
- **Workflow**: `DRAFT` → `IN_EDITORIAL_REVIEW` → `CHANGES_REQUESTED` / `PENDING_ADMIN_APPROVAL` → `PUBLISHED`
- **Immutable revisions** on every content change
- **Append-only workflow audit log** (actor, action, from/to status, note, timestamp)
- **Bootstrap admin** from env vars (`APP_BOOTSTRAP_ADMIN_USERNAME`, `APP_BOOTSTRAP_ADMIN_PASSWORD`)
- **Slug uniqueness**, author isolation, last-admin protection

## Quick Start

### Prerequisites

- Python 3.12 or newer
- Git

### Installation

```bash
# Clone
git clone https://github.com/fnaeiji/27.7-weblog.git
cd 27.7-weblog/my-project

# Create & activate virtual environment
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
# If editable install fails (multiple top-level packages), install directly:
# pip install Django==5.2.4 bcrypt==4.2.1 python-dotenv==1.1.1 markdown-it-py==3.0.0 bleach==6.2.0 pytest==8.3.5 pytest-django==4.9.0 ruff==0.8.6

# Run migrations
python manage.py migrate

# Create initial admin (optional; uses env vars or defaults to admin/adminpass)
# Set env vars first if you want custom credentials:
# $env:APP_BOOTSTRAP_ADMIN_USERNAME="myadmin"
# $env:APP_BOOTSTRAP_ADMIN_PASSWORD="strongpass123"
python manage.py bootstrap_admin

# Start development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ — the public blog homepage.

### Login & Role-Based Panels

| Role | Panel URL | Capabilities |
|------|-----------|--------------|
| **Admin** | `/admin-dashboard/` | Publish/unpublish, user management, all articles |
| **Editor** | `/editor-queue/` | Review queue, request changes, approve, edit |
| **Author** | `/author-dashboard/` | Create/edit drafts, submit for review, history |

Default bootstrap admin: `admin` / `adminpass` (unless overridden by env vars).

## Running Tests

```bash
# Full test suite (44 tests)
python -m pytest -v

# With coverage (if pytest-cov installed)
python -m pytest --cov=blog --cov=workflow --cov=accounts --cov=core

# Specific app
python -m pytest blog/tests/ -v
python -m pytest workflow/tests/ -v
python -m pytest accounts/tests/ -v
```

All tests run against SQLite in-memory, **no external services or API keys required**.

## Code Quality

```bash
# Lint
ruff check .

# Format check
ruff format --check .

# Auto-fix formatting
ruff format .

# Django system checks
python manage.py check

# Migration sanity
python manage.py makemigrations --check --dry-run
```

## Project Structure

```
my-project/
├── blog_project/          # Django project settings (base, dev, prod, test)
├── core/                  # Shared utilities (TimeStampedModel, markdown sanitization)
├── accounts/              # Custom User model (roles), auth views, bootstrap_admin command
├── blog/                  # Article, ArticleRevision models + author/public views
├── workflow/              # WorkflowEvent model + editor/admin views
├── templates/             # Django templates (RTL, Persian UI)
├── static/                # Static assets
├── locale/                # i18n message files
├── specs/                 # Spec Kit feature specifications (future)
├── blog_prd_bundle/       # Source PRDs (FA)
└── manage.py
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `APP_BOOTSTRAP_ADMIN_USERNAME` | Initial admin username | `admin` |
| `APP_BOOTSTRAP_ADMIN_PASSWORD` | Initial admin password | `adminpass` |
| `DJANGO_SETTINGS_MODULE` | Settings module | `blog_project.settings.development` |
| `DATABASE_URL` | Production PostgreSQL URL | (SQLite for dev) |

Create a `.env` file in `my-project/` for local overrides (not committed).

## Production Notes

- Set `DJANGO_SETTINGS_MODULE=blog_project.settings.production`
- Configure `DATABASE_URL` for PostgreSQL
- Set `SECRET_KEY` from a strong random source
- Run `python manage.py collectstatic`
- Use a WSGI server (gunicorn/uWSGI) behind a reverse proxy
- Enable HTTPS, secure cookies, CSRF trusted origins

## Roadmap

- **PRD-02**: AI Writing & Editorial Tools (WritingAgent, ReviewAgent, Mock + OpenAI-compatible providers)
- **PRD-03**: AI Blog Assistant (read-only query tool for authenticated panel users)

## License

MIT — see `LICENSE` file.