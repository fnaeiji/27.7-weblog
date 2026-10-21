# Quickstart: Core Blog & Editorial Workflow

**Feature**: 001-core-blog-workflow
**Date**: 2026-10-19
**Based on**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md)

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | 3.12 or 3.13 recommended |
| pip | 24+ | Bundled with Python |
| Git | 2.40+ | For cloning |
| OS | Linux/macOS/Windows | Any POSIX or Windows |

Optional but recommended:
- `make` — for convenience commands
- `pre-commit` — for git hooks (Ruff, tests)

---

## Project Structure Overview

```
blog_project/
├── manage.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── blog_project/           # Django project settings
├── core/                   # Shared utilities
├── accounts/               # Auth, users, roles
├── blog/                   # Articles, revisions, public pages
├── workflow/               # Editorial workflow, editor/admin views
├── static/                 # CSS, JS
├── templates/              # Global templates
└── locale/                 # Translations (fa)
```

---

## Setup Instructions

### 1. Clone and Enter

```bash
git clone <repository-url> blog_project
cd blog_project
```

### 2. Create Virtual Environment

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (cmd)
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes pytest, Ruff, pre-commit)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required for bootstrap:
# APP_BOOTSTRAP_ADMIN_USERNAME=admin
# APP_BOOTSTRAP_ADMIN_PASSWORD=securepassword123
# Required for Django:
# SECRET_KEY=your-dev-secret-key-here
# DEBUG=True
# Optional:
# DATABASE_URL=sqlite:///db.sqlite3  # default
```

**Example `.env` for development:**
```env
# Bootstrap Admin (used on first run only)
APP_BOOTSTRAP_ADMIN_USERNAME=admin
APP_BOOTSTRAP_ADMIN_PASSWORD=changeme123

# Django
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (SQLite default)
DATABASE_URL=sqlite:///db.sqlite3

# Optional: PostgreSQL for production testing
# DATABASE_URL=postgresql://user:pass@localhost:5432/blogdb
```

### 5. Run Migrations

```bash
# Create database tables
python manage.py migrate

# Verify migration status
python manage.py showmigrations
```

### 6. Create Bootstrap Admin

The bootstrap command runs automatically on first `migrate`/`runserver`, but you can also run it manually:

```bash
# Idempotent — safe to run multiple times
python manage.py bootstrap_admin

# Output: "Bootstrap admin created: admin" or "Admin already exists, skipping"
```

### 7. Run Development Server

```bash
python manage.py runserver

# Or on specific port
python manage.py runserver 8080
```

Server starts at: **http://127.0.0.1:8000/**

---

## Verification Checklist

After starting the server, verify each step:

### Step 1: Public Homepage
- [ ] Open http://127.0.0.1:8000/
- [ ] Page loads with RTL Persian layout
- [ ] No articles shown (empty state)

### Step 2: Admin Login
- [ ] Open http://127.0.0.1:8000/login
- [ ] Log in with bootstrap credentials (`admin` / `changeme123`)
- [ ] Redirected to `/admin/dashboard`
- [ ] Navbar shows "پنل مدیریت" (Admin panel)

### Step 3: Create Author User
- [ ] In Admin panel → "مدیریت کاربران" → "افزودن کاربر"
- [ ] Username: `author1`, Password: `authorpass123`, Role: `نویسنده (AUTHOR)`
- [ ] Save → user appears in list

### Step 4: Author Workflow
- [ ] Log out (top-right menu)
- [ ] Log in as `author1` / `authorpass123`
- [ ] Redirected to `/author/dashboard`
- [ ] Click "مقاله جدید" → fill form:
  - Title: `مقاله اول من`
  - Slug: `my-first-article` (or leave blank for auto)
  - Excerpt: `این یک خلاصه است`
  - Body (Markdown): `# عنوان\n\nمتن مقاله با **مارک‌داون**.`
  - Tags: `تست, وبلاگ`
- [ ] Click "ذخیره پیش‌نویس" → article appears in dashboard with status "پیش‌نویس"
- [ ] Click "ویرایش" → modify body → "ذخیره" → verify revision count increases
- [ ] Click "ارسال برای بررسی" → status changes to "در بررسی ویراستار"

### Step 5: Editor Workflow
- [ ] In Admin panel → create Editor user: `editor1` / `editorpass123`, Role: `ویراستار`
- [ ] Log out, log in as `editor1`
- [ ] Redirected to `/editor/queue`
- [ ] Article "مقاله اول من" appears in queue
- [ ] Click "بررسی" → view article
- [ ] Option A: "درخواست تغییر" with note "لطفاً مقدمه را گسترش دهید" → status → "تغییر درخواست شده"
- [ ] Option B: "تأیید و ارسال به مدیر" → status → "در انتظار تأیید مدیر"

### Step 6: Admin Publish
- [ ] Log in as `admin` (if logged out)
- [ ] Go to `/admin/dashboard` → "مقالات در انتظار تأیید"
- [ ] Article appears with "انتشار" button
- [ ] Click "انتشار" → status → "منتشرشده", `published_at` set
- [ ] Visit homepage → article visible in list
- [ ] Click article slug → detail page shows full content, tags, date

### Step 7: Admin Unpublish
- [ ] In Admin dashboard → "مقالات منتشرشده"
- [ ] Click "لغو انتشار" with note "خطای تایپی در متن"
- [ ] Article status → "پیش‌نویس", removed from homepage immediately
- [ ] Verify 404 on old slug

### Step 8: Revision History
- [ ] As Author/Editor/Admin, open article detail in dashboard
- [ ] Click "تاریخچه" → shows all revisions with editor, date, preview
- [ ] Click "گردش کار" → shows all status transitions with actor, action, note

---

## Running Tests

### All Tests
```bash
# Standard run
pytest

# Verbose with coverage
pytest -v --cov=accounts --cov=blog --cov=workflow --cov=core --cov-report=term-missing

# Parallel (faster)
pytest -n auto
```

### By App
```bash
pytest accounts/tests/
pytest blog/tests/
pytest workflow/tests/
pytest core/tests/
```

### Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Expected Test Results
All **11 mandatory tests** (PRD-01 Section 11) must pass:
1. ✅ Valid and invalid status transitions
2. ✅ Anonymous, Author, Editor, Admin access to sensitive operations
3. ✅ Author cannot access other Author's article
4. ✅ Revision created on content change; not on unchanged save
5. ✅ Publish blocked without editorial review + admin approval
6. ✅ Revision approval invalidated after content edit
7. ✅ Public filter shows only PUBLISHED
8. ✅ Unpublish removes from public pages
9. ✅ Duplicate slug rejected
10. ✅ Markdown with unsafe HTML/JS sanitized
11. ✅ Last active Admin cannot be deactivated/demoted

---

## Code Quality Checks

### Linting (Ruff)
```bash
# Check for errors
ruff check .

# Auto-fix where possible
ruff check . --fix

# Format check
ruff format --check .

# Auto-format
ruff format .
```

### Type Checking (optional, if mypy configured)
```bash
mypy blog_project core accounts blog workflow
```

### Pre-commit (if installed)
```bash
pre-commit run --all-files
```

---

## Common Development Commands

```bash
# Create new migration after model changes
python manage.py makemigrations

# Show SQL for migration
python manage.py sqlmigrate blog 0001

# Django shell
python manage.py shell

# Create superuser manually (alternative to bootstrap)
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic

# Check for deployment issues
python manage.py check --deploy

# View all URLs
python manage.py show_urls

# Run with custom settings
python manage.py runserver --settings=blog_project.settings.production
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure venv activated; run `pip install -r requirements.txt` |
| `django.db.utils.OperationalError: no such table` | Run `python manage.py migrate` |
| Bootstrap admin not created | Check `.env` has both `APP_BOOTSTRAP_ADMIN_USERNAME` and `APP_BOOTSTRAP_ADMIN_PASSWORD`; run `python manage.py bootstrap_admin` manually |
| `TemplateDoesNotExist` | Verify `TEMPLATES['DIRS']` in settings includes project templates dir |
| Static files not loading | Run `python manage.py collectstatic`; check `STATIC_URL`, `STATICFILES_DIRS` |
| RTL not working | Ensure `<html dir="rtl" lang="fa">` in base template; CSS loads `rtl.css` |
| Tests fail with DB errors | Ensure `pytest-django` uses test settings; check `DJANGO_SETTINGS_MODULE` |

---

## Production Deployment Notes

For production, override these settings via environment:

```env
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/blogdb
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Run:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
# Then serve with gunicorn/uwsgi behind nginx
```

---

## Next Steps

After verification, proceed to implementation:
```bash
/speckit.tasks
```

This will generate `tasks.md` with granular implementation tasks for each app, model, view, template, and test.