# Intelligent Blog Platform Constitution

## Core Principles

### I. Python & Sustainable Technologies
- **Primary language:** Python 3.12+.
- **Web framework:** Django 5.2 LTS (latest compatible patch).
- **Templates:** Django Templates for server-rendered UI — no standalone frontend required.
- **Database:** SQLite for local development; PostgreSQL for production via environment-driven settings.
- **ORM & Migrations:** Django ORM with standard migrations.
- **No independent API, separate frontend, extra frameworks, or new dependencies unless a specific requirement justifies them.**
- **No microservices for MVP** — Modular Monolith by default.

### II. Simple Architecture & Clear Responsibility Boundaries
- **Default architecture:** Modular Monolith.
- **Separation of concerns:** Data models, business rules, data access, UI, and external service integrations are distinct layers.
- **Critical business logic** must not live only in views, templates, or UI code.
- **Authorization & workflow rules** enforced in the server-side application layer.
- **Avoid unnecessary abstractions**, complex patterns without real need, and code duplication.
- **Each app/module** owns a single, well-defined responsibility and is independently testable.

### III. Access Control & Editorial Workflow
- **Human roles:** Author, Editor, Admin, and Anonymous Visitor — each with explicit boundaries.
- **Every protected operation** verifies the caller's permissions server-side; hiding buttons in the UI is not sufficient.
- **Authors, Editors, Admins** cannot exceed permissions defined in the PRDs.
- **Publishing** follows the approval rules and role gates defined in PRD-01.
- **Public articles** are visible only when their publication status is valid.
- **Any change** that mutates a reviewed version's content invalidates the prior approval for that version.
- **No AI capability** may bypass human access controls or the editorial approval flow.

### IV. AI Safety & Independence
- **AI capabilities** are isolated behind explicit interfaces/contracts, separable from core logic.
- **Article generation, editorial review, and retrieval assistant** reside in independent services.
- **AI services do not call each other directly**; coordination is handled by the application layer.
- **Configuration, prompts, inputs, and outputs** for each AI capability are independently defined.
- **LLM output is untrusted** until validated against schema and business rules.
- **Expected output structures (e.g., JSON)** are validated for schema and allowed values.
- **AI may propose drafts, review reports, or edit suggestions** — never auto-approve publication.
- **Assistant tools** are scoped, explicit, and governed by the caller's permissions.
- **The assistant must not require unrestricted database access or arbitrary SQL** to answer queries.

### V. Security & Data Protection
- **Use Django's built-in** authentication, authorization, CSRF protection, and session management.
- **All user input** is validated.
- **Markdown or HTML** from users or AI is sanitized before browser rendering.
- **Secrets, passwords, API keys** never stored in repo, source, API responses, or logs.
- **Sensitive settings** read from environment variables.
- **AI assistant** accesses only data the user is authorized to view.
- **Internal errors and stack traces** never shown to public users.
- **Critical security behaviors** covered by automated tests.

### VI. Testability & Code Quality
- **Every new capability** ships with associated tests.
- **Business rules and permissions** tested in isolation from network/external services.
- **AI tests** use Mock/Fake providers — no real API keys, internet, or paid accounts required.
- **Provider errors, timeouts, invalid output, empty responses** are testable scenarios.
- **Regression tests** for publishing rules, versioning, and access control are maintained.
- **Type hints** used throughout; Ruff for lint/formatting.
- **Test structure and run commands** documented in the repository.

### VII. Local Execution & Reproducibility
- **Project runs locally** with documented commands, no external services required for core flows.
- **Mock mode** for all AI capabilities in the current phase provides deterministic behavior.
- **Sample settings file** provided without real secrets.
- **Migrations** suffice to create the database from empty.
- **README** covers prerequisites, dependency install, environment setup, admin bootstrap, migrations, run, and test.
- **No mandatory Docker, Redis, message brokers, or new infra** without justification.

### VIII. User Experience & Accessibility
- **Primary UI language:** Persian (Farsi), RTL layout.
- **English content and mixed Persian/English** render correctly.
- **Responsive UI** with clear loading, success, error, and permission-denied states.
- **High-risk actions** (publish, unpublish) are explicit and understandable.
- **Core features** testable via the simple web UI.
- **No unnecessary frontend framework** imposed.

### IX. Dependency Management & Complexity Control
- **Before adding a dependency**, verify the capability isn't achievable with Django or current libraries.
- **New dependencies** require a clear rationale, version compatibility, and a test strategy.
- **Avoid reimplementing** standard, secure framework features.
- **Tech stack and versions** declared in standard project files (pyproject.toml / requirements.txt).
- **No sweeping dependency upgrades or architecture changes** outside the current feature scope.

### X. Documentation & Phase Completion
- **Each phase** is independently runnable and testable without future phases.
- **Product behavior and feature details** captured in that feature's specification.
- **Plan** explains how the Constitution principles are upheld.
- **Tasks** cover implementation and acceptance tests.
- **Before declaring a feature complete**, related tests run and actual results are reported.
- **Cross-cutting architectural decisions** or multi-feature impacts are documented.

## Additional Constraints

### Technology Stack
- Python 3.12+
- Django 5.2 LTS
- Django Templates (server-rendered)
- SQLite (dev) / PostgreSQL (prod)
- Django ORM + Migrations
- Ruff (lint/format)
- pytest (testing)
- python-dotenv (env management)

### AI Integration Constraints
- AI providers accessed via abstract interfaces (e.g., `AIProvider` protocol).
- Mock/Fake providers mandatory for CI and local dev.
- Real API keys only in production env vars; never in repo.
- Prompt templates versioned alongside code.
- Output validation via Pydantic models or Django forms.

### Data Retention & History
- Article revisions immutable once created.
- Workflow events append-only.
- User deactivation preferred over deletion to preserve history.

## Development Workflow

### Quality Gates
- `ruff check` passes.
- `ruff format --check` passes.
- `pytest` passes (unit + integration).
- No unresolved `TODO`/`FIXME` in changed files.
- Migration files generated and committed for model changes.

### Branching & Commits
- Feature branches from `main`.
- Conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- Constitution amendments via dedicated commit (`docs: amend constitution ...`).

### Spec Kit Integration
- `/speckit.specify` for new features → produces spec in `.specify/specs/`.
- `/speckit.plan` produces implementation plan.
- `/speckit.tasks` breaks plan into executable tasks.
- `/speckit.implement` executes tasks (with human checkpoints).
- Constitution compliance verified at each step.

## Governance

- This Constitution supersedes all other practices for this project.
- **Amendments** require: (1) written proposal, (2) rationale, (3) migration plan for affected code, (4) version bump per semantic versioning.
- **All PRs and reviews** must verify Constitution compliance.
- **Complexity** must be justified against Principles II and IX.
- **Runtime development guidance** lives in `AGENTS.md` and `.specify/memory/` — these must not contradict the Constitution.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19