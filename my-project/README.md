# Persian Blog Platform

A Django-based blog platform with editorial workflow, supporting three human roles: Author, Editor, and Admin.

## Features

- **Public Blog**: Homepage with paginated published articles, article detail pages with Markdown rendering
- **Author Dashboard**: Create/edit drafts, revision tracking, submit for review
- **Editor Queue**: Review submitted articles, request changes, approve, or edit
- **Admin Panel**: Publish (revision-bound), reject, unpublish, user management
- **History & Audit**: Full revision history and workflow event timeline
- **Persian-first RTL UI**: All interfaces in Persian with RTL layout

## Tech Stack

- **Python 3.12+**
- **Django 5.2 LTS**
- **SQLite** (development) / **PostgreSQL** (production)
- **markdown-it-py** + **bleach** for Markdown rendering & sanitization
- **Ruff** for linting/formatting
- **pytest** for testing

## Quick Start

### Prerequisites

- Python 3.12+
- uv (or pip)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd blog_project

# Create virtual environment
uv venv .venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create bootstrap admin (idempotent)
python manage.py bootstrap_admin

# Run development server
python manage.py runserver
```

Server starts at: **http://127.0.0.1:8000/**

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_BOOTSTRAP_ADMIN_USERNAME` | Initial admin username | `admin` |
| `APP_BOOTSTRAP_ADMIN_PASSWORD` | Initial admin password | `change-me-on-first-run` |
| `SECRET_KEY` | Django secret key | `dev-secret-key-not-for-production` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `127.0.0.1,localhost` |
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |

## Verification Steps

After starting the server:

1. **Public Homepage**: Visit `http://127.0.0.1:8000/` — empty blog
2. **Admin Login**: Visit `/login`, login with bootstrap credentials (`admin` / `change-me-on-first-run`)
3. **Role Redirect**: Admin → `/manager/dashboard/`, Editor → `/editor/queue/`, Author → `/author/dashboard/`
4. **Create Author**: In Admin panel → Users → Add user with AUTHOR role
5. **Author Workflow**: Login as Author → Create draft → Edit (creates revisions) → Submit for review
6. **Editor Review**: Login as Editor → Queue → Request changes / Approve
7. **Admin Publish**: Login as Admin → Pending → Publish (revision-bound) / Reject
8. **Unpublish**: Admin → Published → Unpublish → Article returns to DRAFT
9. **History**: View revision & workflow history tabs at any role

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=accounts --cov=blog --cov=workflow --cov=core

# Specific app
pytest accounts/tests/
pytest blog/tests/
pytest workflow/tests/
```

## Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check (if mypy configured)
mypy .
```

## Project Structure

```
blog_project/
├── blog_project/          # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   └── wsgi.py
├── core/                  # Shared utilities
├── accounts/              # Authentication & users
├── blog/                  # Articles, revisions, public pages
├── workflow/              # Editorial workflow, editor/admin views
├── static/                # CSS, JS
├── templates/             # Global templates
└── locale/                # Translations (fa)
```

## Editorial Workflow

```
DRAFT → IN_EDITORIAL_REVIEW → (CHANGES_REQUESTED ↔ IN_EDITORIAL_REVIEW)
  → PENDING_ADMIN_APPROVAL → PUBLISHED
  → (UNPUBLISH) → DRAFT (full re-review required)
```

Key rules:
- Authors create/edit drafts; each content change creates a new revision
- Editors review, request changes (with note), approve, or edit
- Admins publish (only if current revision matches approved revision), reject, or unpublish
- Unpublishing returns article to DRAFT requiring full re-review
- All transitions logged in `WorkflowEvent` with revision binding

## Persian Translations

UI is Persian-first with RTL layout. Translations managed in `locale/fa/LC_MESSAGES/django.po`.

## License

MIT