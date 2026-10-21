# Implementation Plan: Core Blog & Editorial Workflow

**Branch**: `001-core-blog-workflow` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-core-blog-workflow/spec.md`

## Summary

Build a Django 5.2 LTS modular monolith implementing the blog foundation and editorial workflow per PRD-01. The system provides public blog pages (homepage, article detail) and a role-protected content management panel for three human roles (Author, Editor, Admin) with a defined editorial workflow: DRAFT → IN_EDITORIAL_REVIEW → (CHANGES_REQUESTED ↔ IN_EDITORIAL_REVIEW) → PENDING_ADMIN_APPROVAL → PUBLISHED, with unpublish returning to DRAFT. All state transitions are server-enforced, bound to specific article revisions, and audited. No AI integrations in this phase. Runs locally with SQLite; PostgreSQL via settings for production.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**:
- Django 5.2 LTS (latest patch)
- django-environ or python-dotenv for settings
- markdown-it-py or python-markdown for Markdown parsing
- bleach or nh3 for HTML sanitization
- pytest-django for testing
- Ruff for linting/formatting

**Storage**: SQLite (local/dev), PostgreSQL (production) via Django ORM and migrations

**Testing**: pytest with pytest-django; Django test framework for integration tests; Mock/Fake for any external dependencies

**Target Platform**: Linux/macOS/Windows server (any platform supporting Python 3.12+)

**Project Type**: Web application (server-rendered with Django Templates)

**Performance Goals**:
- Homepage and article detail render < 500ms on local hardware
- Support 50 concurrent users in development
- Database queries per page < 20

**Constraints**:
- No external services, API keys, or internet required for core workflow
- No Django REST Framework, Swagger, Redis, Celery, Docker
- No microservices — modular monolith only
- RTL Persian UI primary; English and mixed content supported
- Server-side authorization on every protected operation
- Markdown sanitized to safe HTML before render
- Bootstrap Admin from env vars on first run

**Scale/Scope**:
- 4 core models (User, Article, ArticleRevision, WorkflowEvent)
- ~15 templates (public, auth, author, editor, admin, fragments)
- ~10 views covering all user stories
- 30 functional requirements, 11 acceptance criteria
- 11 mandatory automated tests (PRD-01 Section 11)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python & Sustainable Technologies | ✅ PASS | Python 3.12+, Django 5.2 LTS, Django Templates, SQLite/PostgreSQL, ORM, no microservices |
| II. Simple Architecture & Clear Responsibilities | ✅ PASS | Modular monolith with Django apps: `core`, `accounts`, `blog`, `workflow` |
| III. Access Control & Editorial Workflow | ✅ PASS | Role-based permissions enforced in views/services; workflow transitions validated server-side |
| IV. AI Safety & Independence | ✅ PASS | No AI in this phase; architecture isolates future AI behind interfaces |
| V. Security & Data Protection | ✅ PASS | Django auth, CSRF, sessions; input validation; Markdown sanitization; secrets from env; no stack traces |
| VI. Testability & Code Quality | ✅ PASS | pytest, type hints, Ruff; tests isolated from network; mock AI providers |
| VII. Local Execution & Reproducibility | ✅ PASS | SQLite dev, migrations, documented commands, mock mode for future AI |
| VIII. UX & Accessibility | ✅ PASS | RTL Persian primary, responsive, clear states, explicit high-risk actions |
| IX. Dependency Management & Complexity Control | ✅ PASS | Minimal deps; justify each; use Django built-ins first |
| X. Documentation & Phase Completion | ✅ PASS | Spec complete; plan documents decisions; tasks will cover impl + tests |

**All gates PASS** — no violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-blog-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (empty — no external APIs)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Django Modular Monolith Structure
blog_project/
├── manage.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── blog_project/                 # Project settings package
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                         # Shared utilities, base classes
│   ├── __init__.py
│   ├── models.py                 # Abstract base models (TimeStamped, etc.)
│   ├── views.py                  # Base views, mixins
│   └── utils.py                  # Markdown sanitization, slugify, etc.
├── accounts/                     # User auth, roles, bootstrap
│   ├── __init__.py
│   ├── models.py                 # User model (extends AbstractUser)
│   ├── managers.py               # UserManager
│   ├── views.py                  # Login, logout, profile
│   ├── forms.py                  # Auth forms
│   ├── admin.py                  # Admin registration
│   ├── apps.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_bootstrap.py
│   └── templates/accounts/
│       ├── login.html
│       └── base.html
├── blog/                         # Article CRUD, public pages, revisions
│   ├── __init__.py
│   ├── models.py                 # Article, ArticleRevision
│   ├── views.py                  # Public + Author views
│   ├── forms.py                  # Article forms
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_public_views.py
│   │   ├── test_author_views.py
│   │   └── test_revisions.py
│   └── templates/blog/
│       ├── public/
│       │   ├── home.html
│       │   ├── article_detail.html
│       │   └── 404.html
│       ├── author/
│       │   ├── dashboard.html
│       │   ├── article_form.html
│       │   ├── article_list.html
│       │   └── history.html
│       └── fragments/
│           ├── article_card.html
│           └── revision_list.html
├── workflow/                     # Editorial workflow, Editor/Admin views
│   ├── __init__.py
│   ├── models.py                 # WorkflowEvent
│   ├── views.py                  # Editor queue, review, Admin approve/unpublish
│   ├── forms.py                  # Review forms
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_editor_views.py
│   │   └── test_admin_views.py
│   └── templates/workflow/
│       ├── editor/
│       │   ├── queue.html
│       │   └── review.html
│       └── admin/
│           ├── dashboard.html
│           ├── pending_list.html
│           └── user_management.html
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── rtl.css
│   │   └── components.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── _navbar.html
│   ├── _messages.html
│   └── 403.html
└── locale/
    └── fa/
        └── LC_MESSAGES/
            └── django.po
```

**Structure Decision**: Django modular monolith with 4 apps (`core`, `accounts`, `blog`, `workflow`) following Django best practices. Each app owns its models, views, forms, tests, and templates. Shared utilities in `core`. Project settings split by environment. Static files and global templates at root. This aligns with Constitution Principles I, II, IX.

## Complexity Tracking

No Constitution violations — no complexity tracking required.

---

## Phase 0: Research

### Research Tasks

| Task | Description |
|------|-------------|
| R1 | Confirm Django 5.2 LTS compatibility with Python 3.12+ and select exact patch version |
| R2 | Evaluate Markdown parsers: `markdown-it-py` vs `python-markdown` for safety and extensibility |
| R3 | Evaluate HTML sanitizers: `bleach` vs `nh3` for XSS protection and Django integration |
| R4 | Determine best practice for bootstrap Admin creation (AppConfig.ready vs migration vs management command) |
| R5 | Research Django permission patterns for object-level authorization (guardian vs custom mixins) |
| R6 | Confirm pytest-django configuration for isolated test database (SQLite) |
| R7 | Determine Ruff configuration for Django projects (line length, target version, plugins) |

### Research Output: `research.md`

Each research task produces a decision entry:
```markdown
## R1: Django Version
**Decision**: Django 5.2.4 (latest patch as of 2026-10-19)
**Rationale**: LTS release, security support until April 2027, compatible with Python 3.12+
**Alternatives**: Django 4.2 LTS (older, less features), Django 5.1 (non-LTS)

## R2: Markdown Parser
**Decision**: markdown-it-py with bleach for sanitization
**Rationale**: CommonMark compliant, extensible, active maintenance, bleach integrates well
**Alternatives**: python-markdown (older, less CommonMark compliant)

## R3: HTML Sanitizer
**Decision**: bleach (built on html5lib)
**Rationale**: Django-friendly, configurable allowlist, handles XSS, used by Mozilla
**Alternatives**: nh3 (faster, Rust-based, less Django ecosystem integration)

## R4: Bootstrap Admin
**Decision**: Custom management command `bootstrap_admin` called from AppConfig.ready() with guard
**Rationale**: Runs once on first migrate; idempotent; testable; doesn't require migration data
**Alternatives**: Data migration (harder to test), signal (runs too early)

## R5: Object-Level Permissions
**Decision**: Custom mixins + queryset filtering in views (no django-guardian)
**Rationale**: Simpler, no extra dependency, sufficient for article ownership checks
**Alternatives**: django-guardian (adds dependency, overkill for this scope)

## R6: Test Configuration
**Decision**: pytest-django with `--reuse-db` for speed; SQLite in-memory for unit tests
**Rationale**: Fast, isolated, no external DB needed
**Alternatives**: Django TestCase (slower, less flexible)

## R7: Ruff Config
**Decision**: line-length=100, target-version=py312, preview=true, django plugin
**Rationale**: Matches Constitution (100 cols), modern Python, catches Django issues
**Alternatives**: Black + isort (two tools vs one)
```

---

## Phase 1: Design & Contracts

### Data Model: `data-model.md`

```markdown
# Data Model: Core Blog & Editorial Workflow

## User (accounts.User)
Extends AbstractUser
- id: BigAutoField (PK)
- username: CharField(100, unique=True)
- password: CharField(255)  # hashed by Django auth
- role: CharField(20, choices=Role.choices)  # AUTHOR, EDITOR, ADMIN
- is_active: BooleanField(default=True)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)

Constraints:
- Username unique
- Role enum enforced
- Soft delete via is_active=False (preserves FKs to Article, Revision, WorkflowEvent)

## Article (blog.Article)
- id: BigAutoField (PK)
- author: ForeignKey(User, on_delete=PROTECT, related_name='articles')
- status: CharField(30, choices=Status.choices, default=DRAFT)
- current_revision: PositiveIntegerField(default=0)
- published_at: DateTimeField(null=True, blank=True)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)

Indexes:
- status
- slug (unique via ArticleRevision.slug)
- author_id

Status Enum: DRAFT, IN_EDITORIAL_REVIEW, CHANGES_REQUESTED, PENDING_ADMIN_APPROVAL, PUBLISHED

Methods:
- can_be_edited_by(user): author or editor or admin
- can_be_viewed_by(user): published OR author/editor/admin
- get_current_revision(): returns ArticleRevision

## ArticleRevision (blog.ArticleRevision)
- id: BigAutoField (PK)
- article: ForeignKey(Article, on_delete=CASCADE, related_name='revisions')
- revision_number: PositiveIntegerField()
- title: CharField(255)
- slug: SlugField(255, unique=True)
- excerpt: TextField(blank=True)
- body_markdown: TextField()
- tags: TextField(blank=True)  # comma-separated or JSON array
- created_by: ForeignKey(User, on_delete=PROTECT, related_name='revisions')
- created_at: DateTimeField(auto_now_add=True)

Constraints:
- Unique (article, revision_number)
- Unique slug globally (enforced at DB level)

## WorkflowEvent (workflow.WorkflowEvent)
- id: BigAutoField (PK)
- article: ForeignKey(Article, on_delete=CASCADE, related_name='workflow_events')
- revision: ForeignKey(ArticleRevision, on_delete=SET_NULL, null=True, blank=True, related_name='workflow_events')
- actor: ForeignKey(User, on_delete=PROTECT, related_name='workflow_events')
- action: CharField(40, choices=Action.choices)
- from_status: CharField(30, choices=Article.Status.choices, null=True, blank=True)
- to_status: CharField(30, choices=Article.Status.choices, null=True, blank=True)
- note: TextField(blank=True)
- created_at: DateTimeField(auto_now_add=True)

Action Enum: CREATE, UPDATE_CONTENT, SUBMIT_FOR_REVIEW, REQUEST_CHANGES, APPROVE_EDITORIAL, REJECT_EDITORIAL, PUBLISH, UNPUBLISH, ASSIGN_ROLE, DEACTIVATE_USER

Indexes:
- article_id
- actor_id
```

### Contracts: `contracts/`

No external APIs or CLIs in this phase — server-rendered Django Templates only. Internal contracts (view signatures, form interfaces, model methods) documented in code via type hints and docstrings.

### Quickstart Guide: `quickstart.md`

```markdown
# Quickstart: Core Blog & Editorial Workflow

## Prerequisites
- Python 3.12+
- pip
- git

## Setup

```bash
# Clone and enter
cd blog_project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with:
# APP_BOOTSTRAP_ADMIN_USERNAME=admin
# APP_BOOTSTRAP_ADMIN_PASSWORD=securepassword123
# DEBUG=True
# SECRET_KEY=your-dev-secret-key

# Run migrations
python manage.py migrate

# Create bootstrap admin (idempotent)
python manage.py bootstrap_admin

# Run development server
python manage.py runserver
```

## Verify Installation

1. Open http://127.0.0.1:8000/ — should show empty blog homepage
2. Open http://127.0.0.1:8000/login — login with bootstrap credentials
3. Verify redirect to `/admin/dashboard` (Admin role)
4. Create an Author user in Admin panel
5. Log out, log in as Author — redirect to `/author/dashboard`
6. Create a draft article → submit for review
7. Log in as Editor → review queue → approve
8. Log in as Admin → pending approval → publish
9. Visit homepage → article visible

## Run Tests

```bash
# All tests
pytest

# Specific app tests
pytest accounts/tests/
pytest blog/tests/
pytest workflow/tests/

# With coverage
pytest --cov=accounts --cov=blog --cov=workflow
```

## Expected Outcomes

- All 11 mandatory tests pass (PRD-01 Section 11)
- Ruff check passes: `ruff check .`
- Ruff format passes: `ruff format --check .`
- No migration errors
- Bootstrap admin created only once
```

---

## Re-evaluated Constitution Check (Post-Design)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python & Sustainable Technologies | ✅ PASS | Confirmed: Django 5.2.4, Python 3.12, markdown-it-py, bleach |
| II. Simple Architecture | ✅ PASS | 4 Django apps, clear separation, no over-abstraction |
| III. Access Control & Workflow | ✅ PASS | Custom permission mixins, revision-bound transitions, server enforcement |
| IV. AI Safety | ✅ PASS | No AI; `blog.services.ai` stub interface defined for future |
| V. Security | ✅ PASS | Django auth, CSRF, bleach sanitization, env secrets, no stack traces |
| VI. Testability | ✅ PASS | pytest-django, mocks, isolated SQLite, type hints, Ruff |
| VII. Local Execution | ✅ PASS | SQLite, migrations, bootstrap command, documented quickstart |
| VIII. UX | ✅ PASS | RTL base template, Persian messages, responsive CSS |
| IX. Dependencies | ✅ PASS | 5 direct deps (Django, python-dotenv, markdown-it-py, bleach, pytest-django) |
| X. Documentation | ✅ PASS | Spec, plan, data-model, quickstart; tasks next |

**All gates PASS** — ready for `/speckit.tasks`.