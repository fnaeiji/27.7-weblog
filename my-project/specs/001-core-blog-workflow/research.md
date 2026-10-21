# Research: Core Blog & Editorial Workflow

**Feature**: 001-core-blog-workflow
**Date**: 2026-10-19

---

## R1: Django Version

**Decision**: Django 5.2.4 (latest patch as of 2026-10-19)

**Rationale**: LTS release with security support until April 2027; compatible with Python 3.12+; includes async views, improved ORM, and template enhancements needed for this project.

**Alternatives Considered**:
- Django 4.2 LTS: Older, fewer features, security support until April 2026 (ending soon)
- Django 5.1: Non-LTS, shorter support window
- Django 5.0: Non-LTS, end of life

---

## R2: Markdown Parser

**Decision**: `markdown-it-py` (v3.x) with `bleach` for sanitization

**Rationale**:
- CommonMark compliant with extensive extension ecosystem
- Active maintenance and large community
- Works well with `bleach` for pipeline: Markdown → HTML → Sanitized HTML
- Pure Python, no C extensions (easier deployment)
- Supports plugins for tables, footnotes, etc. if needed later

**Alternatives Considered**:
- `python-markdown`: Older, less CommonMark compliant, slower development
- `mistune`: Fast but less extensible; v3 API breaking changes
- `markdown2`: Less maintained, incomplete CommonMark support

---

## R3: HTML Sanitizer

**Decision**: `bleach` (v6.x) — built on `html5lib`

**Rationale**:
- Django-friendly: used by Mozilla, Read the Docs, many Django projects
- Configurable allowlist (tags, attributes, styles, protocols)
- Handles XSS vectors: script injection, event handlers, javascript: URLs, CSS expression()
- Integrates naturally with markdown-it-py output
- Well-tested, security-focused maintenance

**Alternatives Considered**:
- `nh3`: Faster (Rust-based via PyO3), but less Django ecosystem integration; smaller community
- `lxml.html.clean`: Powerful but complex API; overkill for this use case
- Custom regex: **Rejected** — insecure, incomplete, maintenance burden

**Configuration** (to be implemented in `core.utils.sanitize_html`):
```python
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'blockquote', 'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'hr', 'div', 'span'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'div': ['class'],
    'span': ['class'],
    '*': ['dir']  # for RTL support
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
STRIP_COMMENTS = True
```

---

## R4: Bootstrap Admin Creation

**Decision**: Custom management command `bootstrap_admin` invoked from `accounts.apps.AccountsConfig.ready()` with a guard flag.

**Rationale**:
- Runs automatically on first `migrate`/`runserver` after installation
- Idempotent: checks for existing Admin before creating
- Testable: can be called directly in tests
- No migration data dependency (avoids migration ordering issues)
- Uses environment variables for credentials (never in code)

**Implementation Pattern**:
```python
# accounts/management/commands/bootstrap_admin.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.filter(role=User.Role.ADMIN, is_active=True).exists():
            return
        User.objects.create_superuser(
            username=os.environ['APP_BOOTSTRAP_ADMIN_USERNAME'],
            password=os.environ['APP_BOOTSTRAP_ADMIN_PASSWORD'],
            role=User.Role.ADMIN
        )

# accounts/apps.py
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    _bootstrapped = False

    def ready(self):
        if not self._bootstrapped and not os.environ.get('DJANGO_SKIP_BOOTSTRAP'):
            self._bootstrapped = True
            call_command('bootstrap_admin')
```

**Alternatives Considered**:
- Data migration: Harder to test; runs before models fully ready; credentials in migration file
- Post-migrate signal: Fires on every migrate; harder to guard; timing issues
- Manual command only: Requires developer memory; not reproducible

---

## R5: Object-Level Permissions

**Decision**: Custom permission mixins + queryset filtering in views (no `django-guardian`)

**Rationale**:
- Article ownership checks are simple: `article.author == request.user` or `request.user.is_editor_or_admin`
- Workflow actions require status + role + revision binding — not standard object permissions
- Adding `django-guardian` introduces extra dependency, migration, and complexity for marginal benefit
- Custom mixins are explicit, testable, and follow Django patterns

**Mixin Design**:
```python
# core/views.py
class AuthorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.AUTHOR, User.Role.EDITOR, User.Role.ADMIN]:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class ArticleOwnerOrEditorMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin or self.request.user.is_editor:
            return qs
        return qs.filter(author=self.request.user)

class RevisionBoundActionMixin:
    """Ensure action applies to current revision only"""
    def check_revision_match(self, article, revision_id):
        return article.current_revision == revision_id
```

**Alternatives Considered**:
- `django-guardian`: Adds object permission table, extra queries, migration; overkill for 3 roles
- Django's built-in `UserPassesTestMixin`: Used as base but insufficient for complex workflow rules

---

## R6: Test Configuration

**Decision**: `pytest-django` with SQLite in-memory for unit tests; `--reuse-db` for speed; separate test settings.

**Rationale**:
- `pytest` provides better fixtures, parametrization, and assertion reporting than `unittest`
- `pytest-django` handles Django setup/teardown, database creation, and test discovery
- SQLite in-memory: fast, no external dependency, sufficient for ORM tests
- `--reuse-db` avoids recreation overhead between test runs
- Test settings override: `DEBUG=False`, `SECRET_KEY=test`, `PASSWORD_HASHERS=fast`

**Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "blog_project.settings.test"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--reuse-db -v --tb=short"
testpaths = ["accounts/tests", "blog/tests", "workflow/tests", "core/tests"]

[tool.pytest.django]
reuse_db = true
```

**Alternatives Considered**:
- Django `TestCase`: Slower (transaction per test), less flexible fixtures, no parametrization
- `unittest` with `django.test`: Verbose, limited ecosystem
- Separate test database file: Slower I/O, cleanup issues

---

## R7: Ruff Configuration

**Decision**: `line-length=100`, `target-version=py312`, `preview=true`, with `ruff-django` plugin

**Rationale**:
- 100 columns matches Constitution and team preference
- Python 3.12 target enables modern syntax (match-case, union types, etc.)
- Preview mode catches upcoming lint rules early
- `ruff-django` plugin catches Django-specific issues (model field ordering, migration naming, etc.)
- Single tool replaces `black` + `isort` + `flake8` + `pylint`

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
preview = true
src = ["blog_project", "core", "accounts", "blog", "workflow"]

[tool.ruff.lint]
select = [
    "E", "F", "I", "W", "UP", "B", "C4", "DJ", "DTZ", "T20", "PTH", "ERA", "PL", "TRY", "SIM"
]
ignore = ["DJ01"]  # Allow raw SQL in migrations if needed

[tool.ruff.lint.django]
settings-module = "blog_project.settings.base"

[tool.ruff.format]
quote-style = "single"
indent-style = "space"
skip-magic-trailing-comma = false
```

**Alternatives Considered**:
- `black` + `isort` + `flake8`: Three tools, slower, configuration fragmentation
- `pylint`: Slow, verbose, high false positive rate for Django
- Default Ruff (no Django plugin): Misses framework-specific issues

---

## Summary of Decisions

| Research Item | Decision | Key Rationale |
|---------------|----------|---------------|
| Django Version | 5.2.4 | LTS, Python 3.12+, long support |
| Markdown Parser | markdown-it-py | CommonMark, extensible, active |
| HTML Sanitizer | bleach | Django ecosystem, XSS-safe, configurable |
| Bootstrap Admin | Management command + AppConfig.ready | Idempotent, testable, env-driven |
| Object Permissions | Custom mixins | Simple, no extra deps, explicit |
| Test Config | pytest-django + SQLite | Fast, isolated, modern fixtures |
| Ruff Config | 100 cols, py312, preview, django plugin | Constitution-aligned, single tool |

All `NEEDS CLARIFICATION` items resolved. Ready for Phase 1 design artifacts.