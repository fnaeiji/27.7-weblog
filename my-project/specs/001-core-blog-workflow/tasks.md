---
description: "Task list for Core Blog & Editorial Workflow implementation"
---

# Tasks: Core Blog & Editorial Workflow

**Input**: Design documents from `/specs/001-core-blog-workflow/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Tests are REQUIRED per PRD-01 Section 11 (11 mandatory automated tests) and Constitution Principle VI (Testability & Code Quality).

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1-US6) — required for story phases
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Django project structure

- [X] T001 Create Django project structure per implementation plan at `blog_project/`
- [X] T002 [P] Initialize pyproject.toml with Django 5.2.4, python-dotenv, markdown-it-py, bleach, pytest-django, Ruff at `pyproject.toml`
- [X] T003 [P] Create requirements.txt and requirements-dev.txt from pyproject.toml at `requirements.txt`, `requirements-dev.txt`
- [X] T004 [P] Configure Ruff (line-length=100, target-version=py312, preview=true, django plugin) at `pyproject.toml`
- [X] T005 [P] Configure pytest-django with test settings module at `pyproject.toml`
- [X] T006 [P] Create .env.example with bootstrap admin vars, SECRET_KEY, DEBUG, DATABASE_URL at `.env.example`
- [X] T007 [P] Create base directory structure: `core/`, `accounts/`, `blog/`, `workflow/`, `static/`, `templates/`, `locale/` at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**CRITICAL**: No user story work can begin until this phase is complete

### 2.1 Django Project Configuration

- [X] T008 Create Django settings modules: base.py, development.py, production.py at `blog_project/settings/`
- [X] T009 Configure SQLite (dev) and PostgreSQL (prod) via DATABASE_URL in base.py at `blog_project/settings/base.py`
- [X] T010 Configure Django Templates with RTL Persian support, static files, locale paths at `blog_project/settings/base.py`
- [X] T011 Configure authentication: custom User model (accounts.User), password hashers (BCrypt), login URL at `blog_project/settings/base.py`
- [X] T012 Configure security: CSRF, session, secure headers, allowed hosts at `blog_project/settings/base.py`

### 2.2 Core App - Shared Utilities

- [X] T013 [P] Create TimeStampedModel abstract base at `core/models.py`
- [X] T014 [P] Create slugify utility with Persian support at `core/utils.py`
- [X] T015 [P] Create markdown_to_safe_html pipeline (markdown-it-py → bleach) at `core/utils.py` — **FR-023**
- [X] T016 [P] Create permission mixins: AuthorRequiredMixin, ArticleOwnerOrEditorMixin, RevisionBoundActionMixin at `core/views.py` — **FR-003**
- [X] T017 [P] Create base template with RTL, Persian locale, navbar, messages at `templates/base.html`
- [X] T018 [P] Create fragment templates: _navbar.html, _messages.html, 403.html, 404.html at `templates/`

### 2.3 Accounts App - User Model & Auth

- [X] T019 Create User model extending AbstractUser with role enum (AUTHOR, EDITOR, ADMIN), is_active at `accounts/models.py` — **FR-004, FR-005**
- [X] T020 Create UserManager with create_user, create_superuser, bootstrap_admin at `accounts/managers.py` — **FR-002**
- [X] T021 Create bootstrap_admin management command (idempotent, env-driven) at `accounts/management/commands/bootstrap_admin.py` — **FR-002, FR-008**
- [X] T022 Create login/logout views with role-based redirect at `accounts/views.py` — **FR-001**
- [X] T023 Create login form with username/password, CSRF at `accounts/forms.py`
- [X] T024 Create login template with RTL Persian at `accounts/templates/accounts/login.html`

### 2.4 Database Migrations

- [X] T025 Generate initial migrations for accounts, blog, workflow apps: `python manage.py makemigrations` at project root — accounts done; blog deferred to T037 (Phase 3); workflow blocked (no model-creation task in tasks.md)
- [X] T026 Review and edit migrations: add unique constraints, check constraints, composite indexes per data-model.md at `accounts/migrations/`, `blog/migrations/`, `workflow/migrations/` — accounts done (role index + role check); blog/workflow deferred

### 2.5 Static Assets

- [X] T027 [P] Create base.css with CSS custom properties for theming at `static/css/base.css`
- [X] T028 [P] Create rtl.css with Persian font, RTL layout utilities at `static/css/rtl.css`
- [X] T029 [P] Create components.css for forms, tables, cards, buttons at `static/css/components.css`
- [X] T030 [P] Create minimal main.js for UI interactions (confirm dialogs, form enhancements) at `static/js/main.js`

**Checkpoint**: Foundation ready — run `python manage.py migrate && python manage.py bootstrap_admin && python manage.py runserver` to verify setup

---

## Phase 3: User Story 1 - Anonymous Visitor Reads Published Articles (Priority: P1) **MVP**

**Goal**: Public blog homepage and article detail pages showing only PUBLISHED articles with safe Markdown rendering

**Independent Test**: Visit `/` and `/posts/{slug}` — verify only PUBLISHED articles listed, content renders correctly, unsafe HTML neutralized, 404 for non-published

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T031 [P] [US1] Contract test: public homepage returns 200, uses correct template at `blog/tests/test_public_views.py::test_homepage`
- [X] T032 [P] [US1] Contract test: article detail returns 200 for PUBLISHED, 404 for DRAFT/IN_REVIEW at `blog/tests/test_public_views.py::test_article_detail_access`
- [X] T033 [P] [US1] Integration test: Markdown with `<script>alert(1)</script>` renders as safe text at `blog/tests/test_public_views.py::test_markdown_sanitization` — **SC-009**
- [X] T034 [P] [US1] Integration test: duplicate slug returns 404 without revealing draft at `blog/tests/test_public_views.py::test_draft_not_exposed` — **SC-006**

### Implementation for User Story 1

**Models** (from data-model.md: Article, ArticleRevision)

- [X] T035 [P] [US1] Create Article model with status enum, current_revision, published_at, FK to User at `blog/models.py` — **FR-007, FR-008, FR-019, FR-025**
- [X] T036 [P] [US1] Create ArticleRevision model with revision_number, title, slug (unique), excerpt, body_markdown, tags, FK to Article and User at `blog/models.py` — **FR-009, FR-020, FR-024**
- [X] T037 [US1] Generate and apply migrations for blog app at `blog/migrations/`

**Services/Utils**

- [X] T038 [US1] Implement ArticleManager with published(), by_author(), by_status() querysets at `blog/managers.py` — **FR-011, FR-015**
- [X] T039 [US1] Implement get_current_revision(), can_be_viewed_by(), is_editable() on Article at `blog/models.py` — **FR-022**

**Views & Templates**

- [X] T040 [US1] Create public homepage view: paginated PUBLISHED articles at `blog/views.py`
- [X] T041 [US1] Create article detail view: slug lookup, status check, sanitized HTML rendering at `blog/views.py` — **FR-023, FR-025**
- [X] T042 [US1] Create homepage template: article list with title, excerpt, date, slug at `blog/templates/blog/public/home.html` — **FR-026**
- [X] T043 [US1] Create article detail template: full content, tags, publication date at `blog/templates/blog/public/article_detail.html` — **FR-026**
- [X] T044 [US1] Configure URLs: `/`, `/posts/<slug>/` at `blog/urls.py` and include in project urls at `blog_project/urls.py`

**Checkpoint**: Run server, verify homepage loads, article detail works, Markdown sanitized, drafts return 404

---

## Phase 4: User Story 2 - Author Creates and Manages Drafts (Priority: P1)

**Goal**: Author dashboard, article create/edit with revision tracking, submit for review

**Independent Test**: Login as Author → create draft → edit 3 times (verify revisions) → submit for review → status changes to IN_EDITORIAL_REVIEW

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T045 [P] [US2] Contract test: Author dashboard accessible only to authenticated Author/Editor/Admin at `blog/tests/test_author_views.py::test_dashboard_auth`
- [X] T046 [P] [US2] Integration test: create draft → DRAFT status, revision=1, author_id set at `blog/tests/test_author_views.py::test_create_draft` — **SC-002**
- [X] T047 [P] [US2] Integration test: edit draft with changes → new revision created, previous preserved at `blog/tests/test_author_views.py::test_edit_creates_revision` — **SC-002**
- [X] T048 [P] [US2] Integration test: edit draft without changes → no new revision at `blog/tests/test_author_views.py::test_edit_no_change_no_revision` — **FR-009**
- [X] T049 [P] [US2] Integration test: submit for review → status IN_EDITORIAL_REVIEW, workflow event logged at `blog/tests/test_author_views.py::test_submit_for_review` — **FR-010**
- [X] T050 [P] [US2] Security test: Author cannot access other Author's draft via URL manipulation at `blog/tests/test_author_views.py::test_author_isolation` — **SC-006**
- [X] T051 [P] [US2] Validation test: duplicate slug rejected with error, form data retained at `blog/tests/test_author_views.py::test_duplicate_slug_rejected` — **SC-010**

### Implementation for User Story 2

**Forms**

- [X] T052 [P] [US2] Create ArticleForm: title, slug, excerpt, body_markdown, tags with validation (title, body required; slug unique) at `blog/forms.py` — **FR-008, FR-024**

**Views**

- [X] T053 [US2] Create Author dashboard view: list user's articles with status, revision count at `blog/views.py` — **FR-007**
- [X] T054 [US2] Create article create view: GET form, POST save as DRAFT, create revision 1 at `blog/views.py` — **FR-007, FR-009**
- [X] T055 [US2] Create article edit view: load current revision, compare content, create new revision if changed at `blog/views.py` — **FR-009, FR-020**
- [X] T056 [US2] Create submit_for_review view: validate status (DRAFT/CHANGES_REQUESTED), transition to IN_EDITORIAL_REVIEW, log WorkflowEvent at `blog/views.py` — **FR-010, FR-021**

**Templates**

- [X] T057 [P] [US2] Create author dashboard template: article list with status badges, action buttons at `blog/templates/blog/author/dashboard.html` — **FR-026**
- [X] T058 [P] [US2] Create article form template: create/edit with validation errors, RTL Persian at `blog/templates/blog/author/article_form.html` — **FR-026, FR-027**
- [ ] T059 [P] [US2] Create revision history template: list with number, editor, date, preview at `blog/templates/blog/author/history.html` — **FR-020, FR-021** (Phase 8)

**URLs & Permissions**

- [X] T060 [US2] Configure Author URLs: `/author/dashboard/`, `/author/article/new/`, `/author/article/<id>/edit/`, `/author/article/<id>/submit/` at `blog/urls.py`
- [X] T061 [US2] Apply ArticleOwnerOrEditorMixin to all Author views at `blog/views.py` — **FR-003, FR-004**

**Checkpoint**: Login as Author, create/edit/submit articles, verify revisions and workflow events

---

## Phase 5: User Story 3 - Editor Reviews Submitted Articles (Priority: P1)

**Goal**: Editor review queue, article review with request changes/approve/edit actions

**Independent Test**: Login as Editor → view queue → request changes (with note) → approve → verify workflow events

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T062 [P] [US3] Contract test: Editor queue accessible only to Editor/Admin at `workflow/tests/test_editor_views.py::test_queue_auth`
- [ ] T063 [P] [US3] Integration test: Editor queue shows only IN_EDITORIAL_REVIEW articles ordered by update time at `workflow/tests/test_editor_views.py::test_queue_listing` — **FR-011**
- [ ] T064 [P] [US3] Integration test: request changes with note → CHANGES_REQUESTED, workflow event logged at `workflow/tests/test_editor_views.py::test_request_changes` — **FR-012, FR-021**
- [ ] T065 [P] [US3] Integration test: approve editorial → PENDING_ADMIN_APPROVAL, workflow event logged at `workflow/tests/test_editor_views.py::test_approve_editorial` — **FR-013**
- [ ] T066 [P] [US3] Integration test: edit during review → new revision, status DRAFT, workflow event logged at `workflow/tests/test_editor_views.py::test_edit_during_review` — **FR-014**
- [ ] T067 [P] [US3] Security test: Editor cannot publish directly (no UI, server rejects) at `workflow/tests/test_editor_views.py::test_editor_cannot_publish` — **FR-016, SC-006**

### Implementation for User Story 3

**Forms**

- [ ] T068 [P] [US3] Create ReviewForm: action (request_changes/approve), note (required for request_changes) at `workflow/forms.py` — **FR-012**

**Views**

- [ ] T069 [US3] Create Editor queue view: list IN_EDITORIAL_REVIEW articles with title, author, updated_at at `workflow/views.py` — **FR-011**
- [ ] T070 [US3] Create article review view: GET shows article with sanitized HTML, POST handles request_changes/approve/edit at `workflow/views.py` — **FR-012, FR-013, FR-014**
- [ ] T071 [US3] Implement request_changes: validate note, transition to CHANGES_REQUESTED, log WorkflowEvent with note at `workflow/views.py` — **FR-012, FR-021**
- [ ] T072 [US3] Implement approve_editorial: transition to PENDING_ADMIN_APPROVAL, log WorkflowEvent bound to current revision at `workflow/views.py` — **FR-013, FR-022**
- [ ] T073 [US3] Implement edit_during_review: create new revision, revert to DRAFT, log WorkflowEvent at `workflow/views.py` — **FR-014, FR-020**

**Templates**

- [ ] T074 [P] [US3] Create editor queue template: table with article title, author, updated, actions at `workflow/templates/workflow/editor/queue.html` — **FR-026**
- [ ] T075 [P] [US3] Create editor review template: article content, review form with note field at `workflow/templates/workflow/editor/review.html` — **FR-026**

**URLs & Permissions**

- [ ] T076 [US3] Configure Editor URLs: `/editor/queue/`, `/editor/article/<id>/review/` at `workflow/urls.py`
- [ ] T077 [US3] Apply Editor/Admin permission checks to all Editor views at `workflow/views.py` — **FR-003, FR-004**

**Checkpoint**: Login as Editor, review queue works, request_changes/approve/edit all function correctly

---

## Phase 6: User Story 4 - Admin Approves and Publishes Articles (Priority: P1)

**Goal**: Admin pending approval list, publish (revision-bound), reject, unpublish with full re-review requirement

**Independent Test**: Login as Admin → view pending → publish (only if revision matches) → reject with note → unpublish published article → verify public removal

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T078 [P] [US4] Contract test: Admin dashboard accessible only to Admin at `workflow/tests/test_admin_views.py::test_admin_dashboard_auth`
- [ ] T079 [P] [US4] Integration test: publish succeeds only when revision matches reviewed revision at `workflow/tests/test_admin_views.py::test_publish_revision_match` — **SC-004**
- [ ] T080 [P] [US4] Integration test: publish rejected with error when content edited after editorial review at `workflow/tests/test_admin_views.py::test_publish_stale_revision_rejected` — **SC-004**
- [ ] T081 [P] [US4] Integration test: reject with note → CHANGES_REQUESTED, workflow event logged at `workflow/tests/test_admin_views.py::test_admin_reject` — **FR-017**
- [ ] T082 [P] [US4] Integration test: unpublish → DRAFT, published_at cleared, removed from public pages at `workflow/tests/test_admin_views.py::test_unpublish` — **SC-005**
- [ ] T083 [P] [US4] Security test: last active Admin cannot be deactivated/demoted at `accounts/tests/test_bootstrap.py::test_last_admin_protection` — **SC-011**

### Implementation for User Story 4

**Forms**

- [ ] T084 [P] [US4] Create AdminActionForm: action (publish/reject/unpublish), note (required for reject/unpublish) at `workflow/forms.py` — **FR-017, FR-018**

**Views**

- [ ] T085 [US4] Create Admin dashboard view: stats, pending approval list, published list, user management link at `workflow/views.py` — **FR-015**
- [ ] T086 [US4] Create pending approval list view: PENDING_ADMIN_APPROVAL articles with publish/reject actions at `workflow/views.py` — **FR-015**
- [ ] T087 [US4] Implement publish action: verify revision match, transition to PUBLISHED, set published_at, log WorkflowEvent bound to revision at `workflow/views.py` — **FR-016, FR-019, FR-022**
- [ ] T088 [US4] Implement reject action: validate note, transition to CHANGES_REQUESTED, log WorkflowEvent at `workflow/views.py` — **FR-017, FR-021**
- [ ] T089 [US4] Implement unpublish action: validate note, transition to DRAFT, clear published_at, log WorkflowEvent at `workflow/views.py` — **FR-018, FR-019, FR-021**

**Templates**

- [ ] T090 [P] [US4] Create admin dashboard template: stats cards, pending table, published table at `workflow/templates/workflow/admin/dashboard.html` — **FR-026**
- [ ] T091 [P] [US4] Create pending approval template: article preview, publish/reject buttons at `workflow/templates/workflow/admin/pending_list.html` — **FR-026**
- [ ] T092 [P] [US4] Create user management template: user list, create/edit/deactivate, role assign at `workflow/templates/workflow/admin/user_management.html` — **FR-004**

**URLs & Permissions**

- [ ] T093 [US4] Configure Admin URLs: `/admin/dashboard/`, `/admin/pending/`, `/admin/published/`, `/admin/users/` at `workflow/urls.py`
- [ ] T094 [US4] Apply Admin-only permission checks to all Admin views at `workflow/views.py` — **FR-003, FR-004**

**Checkpoint**: Login as Admin, publish/reject/unpublish work correctly, revision binding enforced

---

## Phase 7: User Story 5 - User Authentication and Role Management (Priority: P1)

**Goal**: Login/logout, bootstrap Admin, Admin user management (create, deactivate, assign roles)

**Independent Test**: Fresh DB → bootstrap Admin created → login redirects by role → Admin manages users → inactive users blocked

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T095 [P] [US5] Contract test: login page accessible, POST authenticates at `accounts/tests/test_views.py::test_login`
- [ ] T096 [P] [US5] Integration test: bootstrap Admin created on first run, not duplicated at `accounts/tests/test_bootstrap.py::test_bootstrap_admin` — **SC-008**
- [ ] T097 [P] [US5] Integration test: role-based redirect (Admin→/admin/dashboard, Editor→/editor/queue, Author→/author/dashboard) at `accounts/tests/test_views.py::test_role_redirect` — **SC-006**
- [ ] T098 [P] [US5] Integration test: inactive user login denied at `accounts/tests/test_views.py::test_inactive_user_blocked` — **FR-004**
- [ ] T099 [P] [US5] Integration test: Admin creates user with AUTHOR role → user can login and access Author features at `accounts/tests/test_bootstrap.py::test_admin_create_user` — **FR-004**

### Implementation for User Story 5

**Views** (extend from Phase 2)

- [ ] T100 [US5] Enhance login view: role-based redirect using authentication_success_handler pattern at `accounts/views.py` — **FR-001**
- [ ] T101 [US5] Create logout view with secure session invalidation at `accounts/views.py`
- [ ] T102 [US5] Create Admin user management views: list, create, edit (role, active), deactivate at `workflow/views.py` — **FR-004, FR-005**
- [ ] T103 [US5] Implement last Admin protection in deactivate/role-change logic at `accounts/managers.py` or `workflow/views.py` — **FR-005, FR-006**

**Templates** (extend from Phase 2)

- [ ] T104 [P] [US5] Enhance login template: error messages, RTL Persian at `accounts/templates/accounts/login.html` — **FR-027**

**URLs**

- [ ] T105 [US5] Configure auth URLs: `/login`, `/logout` at `accounts/urls.py` and include in project urls

**Checkpoint**: Full auth flow works, bootstrap Admin, role redirects, user management, last Admin protection

---

## Phase 8: User Story 6 - Article History and Audit Trail (Priority: P2)

**Goal**: Revision history and workflow event history for articles, accessible to authorized roles

**Independent Test**: View history tabs for any article as Author/Editor/Admin → see all revisions and workflow events chronologically

### Tests for User Story 6

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T106 [P] [US6] Integration test: revision history shows all revisions with number, editor, date, preview at `blog/tests/test_revisions.py::test_revision_history` — **FR-020**
- [ ] T107 [P] [US6] Integration test: workflow history shows all events with actor, action, from/to, note, timestamp at `workflow/tests/test_admin_views.py::test_workflow_history` — **FR-021**
- [ ] T108 [P] [US6] Security test: unauthorized user cannot view history at `blog/tests/test_revisions.py::test_history_access_control` — **SC-006**

### Implementation for User Story 6

**Views**

- [ ] T109 [US6] Create revision history view: list ArticleRevision for article with content preview at `blog/views.py` — **FR-020**
- [ ] T110 [US6] Create workflow history view: list WorkflowEvent for article chronologically at `workflow/views.py` — **FR-021**
- [ ] T111 [US6] Add history tabs/links to Author, Editor, Admin article detail views at `blog/views.py`, `workflow/views.py`

**Templates**

- [ ] T112 [P] [US6] Create revision history template: table with revision#, editor, date, preview link at `blog/templates/blog/author/history.html` (extend) — **FR-026**
- [ ] T113 [P] [US6] Create workflow history template: timeline with actor, action, from→to, note, timestamp at `workflow/templates/workflow/admin/history.html` — **FR-026**

**URLs & Permissions**

- [ ] T114 [US6] Configure history URLs: `/author/article/<id>/history/`, `/editor/article/<id>/history/`, `/admin/article/<id>/history/` at `blog/urls.py`, `workflow/urls.py`
- [ ] T115 [US6] Apply ArticleOwnerOrEditorMixin to history views at `blog/views.py`, `workflow/views.py` — **FR-003**

**Checkpoint**: History views work for all authorized roles, show complete audit trail

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, validation, documentation

- [ ] T116 [P] Run full test suite: `pytest -v --cov=accounts --cov=blog --cov=workflow --cov=core` — **SC-007**
- [ ] T117 [P] Run Ruff check and format: `ruff check . && ruff format --check .` — Constitution Principle VI
- [ ] T118 [P] Run quickstart.md validation steps manually (all 8 verification steps) — **SC-001 through SC-011**
- [ ] T119 [P] Create Persian translations for all user-facing strings at `locale/fa/LC_MESSAGES/django.po` — **FR-026**
- [ ] T120 [P] Add Django admin registration for all models at `accounts/admin.py`, `blog/admin.py`, `workflow/admin.py`
- [ ] T121 [P] Create README.md with setup, run, test commands at repository root
- [ ] T122 [P] Verify all 11 PRD-01 Section 11 mandatory tests pass:
  - Status transitions (valid/invalid) — T031, T049, T064, T065, T079, T080, T082
  - Access control (4 roles) — T045, T050, T062, T067, T078, T083, T097, T098, T108
  - Author isolation — T050
  - Revision creation — T047, T048
  - Publish without review/approval blocked — T079, T080
  - Revision invalidation after edit — T073, T079, T080
  - Public PUBLISHED filter — T032
  - Unpublish removes from public — T082
  - Unique slug — T051
  - Markdown sanitization — T033
  - Last Admin protection — T083
- [ ] T123 [P] Test SQLite and PostgreSQL (via Docker) migrations apply cleanly — **FR-029, FR-030**
- [ ] T124 [P] Verify no secrets in code, .env.example has no real values — Constitution Principle V

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — **BLOCKS all user stories**
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1 (Phase 3) — MVP, can start after Foundational
  - US2 (Phase 4) — Depends on Foundational; shares Article/ArticleRevision models with US1
  - US3 (Phase 5) — Depends on Foundational; uses Article, ArticleRevision, WorkflowEvent
  - US4 (Phase 6) — Depends on Foundational; uses all models
  - US5 (Phase 7) — Depends on Foundational (Accounts); can start early
  - US6 (Phase 8) — Depends on Foundational; uses ArticleRevision, WorkflowEvent
- **Polish (Phase 9)**: Depends on all desired user stories complete

### User Story Dependencies

| Story | Can Start After | Dependencies |
|-------|-----------------|--------------|
| US1 (P1) | Phase 2 | None — **MVP** |
| US2 (P1) | Phase 2 | Shares Article/ArticleRevision models with US1 |
| US3 (P1) | Phase 2 | Needs Article, ArticleRevision, WorkflowEvent models |
| US4 (P1) | Phase 2 | Needs all models |
| US5 (P1) | Phase 2 | Accounts app only — **can start in parallel with US1** |
| US6 (P2) | Phase 2 | Needs ArticleRevision, WorkflowEvent models |

### Within Each User Story

1. Tests (if included) MUST be written and FAIL before implementation
2. Models → Services/Managers → Forms → Views → Templates → URLs
3. Core implementation before integration
4. Story complete before moving to next priority (sequential) OR parallel if staffed

---

## Parallel Opportunities

- **All Phase 1 tasks marked [P]**: Can run in parallel (T002-T007)
- **All Phase 2 tasks marked [P]**: Can run in parallel within Phase 2 (T013-T018, T027-T030)
- **All test tasks marked [P] within a story**: Can run in parallel (e.g., T031-T034 for US1)
- **All template tasks marked [P] within a story**: Can run in parallel (e.g., T057-T059 for US2)
- **Once Phase 2 completes**: US1, US5 can start in parallel (different apps: blog vs accounts)
- **US2, US3, US4**: Can proceed in parallel after US1 models exist (different view/template files)

### Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test: public homepage returns 200" (T031)
Task: "Contract test: article detail access control" (T032)
Task: "Integration test: Markdown sanitization" (T033)
Task: "Integration test: draft not exposed" (T034)

# Launch all models for User Story 1 together:
Task: "Create Article model" (T035)
Task: "Create ArticleRevision model" (T036)
```

### Parallel Example: User Story 5 (Authentication)

```bash
# Can run in parallel with US1 since it uses different app (accounts):
Task: "Contract test: login page" (T095)
Task: "Integration test: bootstrap Admin" (T096)
Task: "Integration test: role redirect" (T097)
Task: "Integration test: inactive user blocked" (T098)
Task: "Integration test: Admin creates user" (T099)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (Anonymous public pages)
4. **STOP and VALIDATE**: Test US1 independently per quickstart.md
5. Deploy/demo if ready — **this is a working blog!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (MVP!)
3. Add US5 (Auth) → Test independently → Deploy/Demo
4. Add US2 (Author) → Test independently → Deploy/Demo
5. Add US3 (Editor) → Test independently → Deploy/Demo
6. Add US4 (Admin) → Test independently → Deploy/Demo
7. Add US6 (History) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy (3+ developers)

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Public) + US2 (Author) — blog app
   - Developer B: US5 (Auth) + US4 (Admin) — accounts + workflow apps
   - Developer C: US3 (Editor) + US6 (History) — workflow + blog apps
3. Stories integrate via shared models; merge frequently

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable per spec.md
- Verify tests fail before implementing (TDD per Constitution Principle VI)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All 11 PRD-01 mandatory tests mapped to specific test tasks above
- File paths use Django modular monolith structure from plan.md