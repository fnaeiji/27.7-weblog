# Repository Instructions — AI Blog Platform

## 1. Project goal and sources of truth

This repository contains a Persian-first blog application with author, editor, and administrator roles, plus independently delivered AI-assisted editorial and blog-assistant features.

Use these sources in this order:
1. The user's latest explicit decisions and approvals.
2. `.specify/memory/constitution.md` for durable project principles.
3. The active feature's Spec Kit artifacts (`spec.md`, `plan.md`, `tasks.md`, contracts, data model, and checklists).
4. The relevant approved PRD for product behavior.
5. This file for working conventions and implementation defaults.

If sources conflict, do not silently pick one. Explain the conflict and stop before making an architectural or product decision that would be hard to reverse. A PRD may define product behavior; it must not silently override a later explicit technology decision.

**Known migration decision:** The earlier PRDs and roadmap were originally written for Java/Spring. The project direction is now Python. Before planning implementation, reconcile the PRDs and roadmap with the approved Python stack while preserving product requirements. Do not generate a Java/Spring plan or code. If you are not explicitly authorized to edit the PRDs in the current task, report the conflict and ask for permission rather than silently changing them.

## 2. Technology defaults

Unless the user approves a change:
- Python 3.12 or newer.
- Django 5.2 LTS, using the latest compatible patch release.
- Django Templates for the primary web UI; keep the MVP in one deployable Django application.
- SQLite for zero-setup local development and tests; PostgreSQL for deployment and PostgreSQL-specific verification where required.
- Django ORM and migrations for persistence.
- Django built-in authentication, sessions, CSRF protection, and permission mechanisms where appropriate.
- Django's built-in test framework as the default. Use `pytest`/`pytest-django` only if already adopted or justified in the plan.
- Ruff for Python linting and formatting, unless the repository already has an equivalent configured tool.
- Use a virtual environment and a committed, reproducible dependency definition (`pyproject.toml` or the repository's existing standard).

Do not add FastAPI, Django REST Framework, a separate JavaScript frontend, Celery, Redis, Docker, a vector database, or other infrastructure merely by preference. Add them only when a requirement in the active feature justifies them and the plan records the reason. Add Django REST Framework and OpenAPI/Swagger only if a genuine REST API is in scope; Swagger is not a replacement for testing the web UI.

## 3. Spec Kit workflow

- Follow the Spec Kit command names, templates, and workflow available in this repository's installed version. Do not assume command aliases or features; inspect the generated command instructions if uncertain.
- Work on **one feature / one PRD at a time**. Identify the active feature directory before modifying any `spec.md`, `plan.md`, or `tasks.md`. Do not infer the active feature from the Git branch name alone.
- `/speckit.specify` should capture user-visible behavior, goals, requirements, and acceptance criteria. Avoid choosing implementation technology in the product spec unless it is a product constraint.
- Use `/speckit.clarify` when consequential ambiguity remains. Ask focused questions and wait for the user's answers instead of inventing business rules.
- `/speckit.plan` must follow the Python/Django defaults above, record important architecture and dependency decisions, and explain any proposed deviation.
- Generate tasks from the approved spec and plan. Run the available consistency-analysis command (normally `/speckit.analyze`) before implementation. Resolve findings at the source artifact and rerun analysis until no material contradiction remains.
- Do not start implementation before the user has had an opportunity to review the spec and plan. Do not run the entire implementation in one go for a multi-phase feature; implement a coherent phase or story, verify it, report the result, then continue.
- Keep the active feature's changes scoped to that feature. Do not rewrite unrelated specs, PRDs, or infrastructure.
- If the installed Spec Kit version names a command differently, use the installed official equivalent and tell the user which command name was used.

## 4. Architecture and code quality

- Use a modular monolith. Keep domain rules in clear service/domain functions or model methods rather than burying them entirely in views or templates.
- Prefer Django's built-in features and simple explicit code over extra abstractions.
- Add type hints to new Python functions when useful and practical.
- Validate data at system boundaries. Return clear, safe user-facing errors; do not leak stack traces or secrets.
- Keep views/controllers thin. Do not create a generic repository/service framework unless the current feature needs it.
- Never run destructive database operations or drop/reset development data without explicit approval.
- Do not introduce dependencies, config systems, background workers, or external services outside the active feature's scope.

## 5. Product and AI safety rules

- Human authorization governs editorial approval and publication. AI output is a suggestion or draft, not approval to publish.
- Only authorized roles can access drafts, editorial reports, admin functions, and private assistant context. Enforce this server-side, not only by hiding UI controls.
- Every material article-content edit must create a new revision or otherwise invalidate approval of the previous revision, according to the approved spec.
- AI-generated output is untrusted input. Validate structured output, sanitize rendered rich text/Markdown, and do not execute model-provided code or HTML.
- AI provider settings and prompts must be isolated behind focused interfaces/adapters. Use a deterministic Mock/Fake provider for tests and local demos; core workflows must not require a real API key or network connection.
- AI capabilities must not bypass user permissions, directly call other AI agents, publish content automatically, run arbitrary SQL, or access unrestricted database records.
- Read-only assistant tools must be allowlisted, validate arguments, and apply the same user-level authorization as the ordinary UI.
- Never log API keys, passwords, tokens, full secret-bearing headers, or other credentials.

## 6. Required verification

Before declaring an implementation unit complete:
1. Read `git status` and inspect the diff, including changes made before the current task.
2. Run the focused tests for the changed behavior.
3. Run the full test suite when reasonably practical; otherwise state clearly what was not run and why.
4. Run Ruff checks when configured, and run Django system checks and migration checks when relevant.
5. Check for unintended schema changes, exposed secrets, unsafe rendering, missing authorization checks, and unrelated file edits.
6. Use `git diff --check`.
7. Report the exact commands executed and whether they passed. Never claim a test passed if it was not run.

Typical commands after project setup (adjust only to match actual project configuration):
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test`
- `ruff check .`
- `ruff format --check .`
- `git diff --check`

Do not invent passing results when a dependency or environment is missing. Explain the blocker and the exact command the user can run.

## 7. Git workflow — commits allowed, push requires explicit approval

At the start of a task:
- Check `git status --short`, current branch, recent commits, and configured remotes.
- Preserve all user changes. Never discard, overwrite, reset, or stage pre-existing user changes just to get a clean working tree.
- Do not add, change, or infer a remote URL. If no remote is configured, ask the user for the intended repository URL before configuring one.
- Do not switch branches without a clear reason; never make assumptions that a branch change means the active Spec Kit feature changed.

After each **coherent implementation unit** (for example, one completed task group or user story):
- Run the relevant checks and inspect the complete diff.
- Stage only the files that belong to that unit, by explicit path. Do not blindly use `git add .` or `git add -A` when unrelated or pre-existing changes may be present. Never commit `.env`, API keys, credentials, private certificates, local databases, or other machine-specific/private data; inspect staged changes for secrets first.
- If the change is correct, tests/checks pass, and the staged diff contains only the intended changes, create a local commit automatically.
- Use a concise imperative commit message, such as `feat(blog): add article draft workflow` or `test(ai): cover mock review flow`.
- If tests fail, the diff contains unrelated changes, a secret is detected, or the scope is unclear, do not commit; report the blocker.
- Never amend, rebase, force-reset, delete a branch, discard changes, or rewrite Git history unless the user explicitly authorizes that specific action.

**Remote operations:** Never run `git push`, open/update a remote PR, publish a release, or otherwise change remote state unless the user has explicitly approved that exact push/remote action after reviewing the proposed commit(s) and target remote/branch. A general request to implement a feature is not permission to push. Before requesting approval, report the branch, remote, target branch, commits to be pushed, and test status. If approval is not given, leave commits local and stop. Never force-push unless the user explicitly authorizes the force-push itself.

Important: these are agent instructions, not a security boundary. Use the coding agent's permission/approval configuration as a second control. Do not run OpenCode in auto-approve mode when you require a human approval prompt for `git push`.

## 8. Scope and user communication

- Do only the current requested phase. Do not silently continue from planning into implementation.
- For high-impact choices, missing credentials, uncertain destructive actions, unclear permissions, or PRD/Constitution conflicts, pause and ask the user.
- Do not ask the user to approve routine, reversible code edits within the already approved feature; do ask before remote operations and destructive actions as specified above.
- Keep progress reports short and factual. At the end, summarize files changed, implementation completed, checks run, failures/blockers, commit hash/message (if committed), and whether anything was pushed (normally no).
