# Feature Specification: Core Blog & Editorial Workflow

**Feature Branch**: `001-core-blog-workflow`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "PRD-01 - Core Blog, Roles & Content Workflow. Build a blog with public pages and content management panel. Three human roles: Author, Editor, Admin. Author creates drafts; Editor reviews and approves or requests changes; Admin makes final publish decision. Anonymous visitors see only published articles. No AI services in this phase. Must run locally without API keys or internet."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Anonymous Visitor Reads Published Articles (Priority: P1)

A visitor browses the public blog homepage, sees a list of published articles with title, excerpt, publication date, and slug. They click an article to read the full content including title, excerpt, body, tags, and publication date.

**Why this priority**: This is the primary public-facing value of the blog — readable content for visitors.

**Independent Test**: Can be fully tested by visiting `/` and `/posts/{slug}` and verifying only PUBLISHED articles appear, with correct content rendering.

**Acceptance Scenarios**:

1. **Given** published articles exist, **When** visitor accesses `/`, **Then** only PUBLISHED articles are listed with title, excerpt, publication date, slug
2. **Given** a published article with slug `my-article`, **When** visitor accesses `/posts/my-article`, **Then** full article content displays with title, excerpt, body, tags, publication date
3. **Given** a draft or in-review article, **When** visitor accesses its slug, **Then** 404 is returned without revealing the article exists
4. **Given** article body contains Markdown with unsafe HTML/JS, **When** rendered, **Then** only safe HTML is output; scripts are neutralized

---

### User Story 2 - Author Creates and Manages Drafts (Priority: P1)

An authenticated Author creates a new article draft with title, slug, excerpt, body (Markdown), and tags. The draft is saved with DRAFT status. The Author can edit their own drafts, save changes (creating new revisions when content changes), and submit for editorial review.

**Why this priority**: Content creation is the starting point of the editorial workflow.

**Independent Test**: Can be fully tested by logging in as Author, creating a draft, editing it, verifying revision history, and submitting for review.

**Acceptance Scenarios**:

1. **Given** Author is logged in, **When** they create a new article with required fields, **Then** article is saved as DRAFT with revision 1, author_id set to current user
2. **Given** Author edits their own draft and changes content, **When** saved, **Then** new revision created with incremented number; previous revision preserved
3. **Given** Author edits their own draft without content changes, **When** saved, **Then** no new revision created
4. **Given** Author submits draft for review, **When** submitted, **Then** status changes to IN_EDITORIAL_REVIEW; workflow event logged
5. **Given** Author tries to access another Author's draft via URL manipulation, **When** request made, **Then** access denied (403/404)
6. **Given** duplicate slug submitted, **When** save attempted, **Then** validation error shown; form data preserved

---

### User Story 3 - Editor Reviews Submitted Articles (Priority: P1)

An authenticated Editor views a queue of articles in IN_EDITORIAL_REVIEW status. They can read the article, make content edits (creating new revisions), request changes with a mandatory note (moving to CHANGES_REQUESTED), or approve editorial review (moving to PENDING_ADMIN_APPROVAL).

**Why this priority**: Editorial review is the mandatory gate before admin approval.

**Independent Test**: Can be fully tested by logging in as Editor, accessing the review queue, and performing each review action.

**Acceptance Scenarios**:

1. **Given** Editor is logged in, **When** they access `/editor/queue`, **Then** only IN_EDITORIAL_REVIEW articles listed, ordered by update time
2. **Given** Editor opens an article in review, **When** they request changes with a note, **Then** status becomes CHANGES_REQUESTED; workflow event logged with note
3. **Given** Editor opens an article in review, **When** they approve without changes, **Then** status becomes PENDING_ADMIN_APPROVAL; workflow event logged
4. **Given** Editor edits article content during review, **When** saved, **Then** new revision created; status reverts to DRAFT; workflow event logged
5. **Given** Editor tries to publish directly, **When** attempted, **Then** action not available (no UI, server rejects)

---

### User Story 4 - Admin Approves and Publishes Articles (Priority: P1)

An authenticated Admin views articles in PENDING_ADMIN_APPROVAL. They can publish (if current revision matches reviewed revision) or reject with a note (moving to CHANGES_REQUESTED). Admin can also unpublish published articles (moving to DRAFT, requiring full re-review).

**Why this priority**: Admin approval is the final gate for publication; unpublish is a critical safety operation.

**Independent Test**: Can be fully tested by logging in as Admin, accessing pending approval list, publishing and unpublishing articles.

**Acceptance Scenarios**:

1. **Given** Admin is logged in, **When** they access pending approval list, **Then** only PENDING_ADMIN_APPROVAL articles shown
2. **Given** article in PENDING_ADMIN_APPROVAL with current revision matching reviewed revision, **When** Admin publishes, **Then** status becomes PUBLISHED; published_at set; workflow event logged
3. **Given** article in PENDING_ADMIN_APPROVAL where content was edited after editorial review, **When** Admin attempts to publish, **Then** publish rejected; validation error shown
4. **Given** Admin rejects with note, **When** submitted, **Then** status becomes CHANGES_REQUESTED; workflow event logged with note
5. **Given** published article, **When** Admin unpublishes with note, **Then** status becomes DRAFT; published_at cleared; article immediately removed from public pages; workflow event logged
6. **Given** last active Admin, **When** they attempt to deactivate or demote themselves, **Then** action rejected

---

### User Story 5 - User Authentication and Role Management (Priority: P1)

Users log in via `/login`. On first run with no Admin, a bootstrap Admin is created from environment variables. Admin can create, deactivate, and assign roles (AUTHOR, EDITOR, ADMIN) to users. Inactive users cannot log in.

**Why this priority**: Authentication and authorization are foundational to all other stories.

**Independent Test**: Can be fully tested by running fresh instance (bootstrap Admin created), logging in, managing users, verifying inactive users blocked.

**Acceptance Scenarios**:

1. **Given** fresh database with no users, **When** application starts with bootstrap env vars set, **Then** Admin user created with configured credentials
2. **Given** bootstrap Admin exists, **When** application restarts, **Then** no duplicate Admin created
3. **Given** user logs in with correct credentials, **When** authenticated, **Then** redirected to role-appropriate dashboard (Admin→/admin/dashboard, Editor→/editor/queue, Author→/author/dashboard)
4. **Given** inactive user attempts login, **When** credentials submitted, **Then** login denied
5. **Given** Admin creates new user with AUTHOR role, **When** saved, **Then** user can log in and access Author features only

---

### User Story 6 - Article History and Audit Trail (Priority: P2)

For any article, Author, Editor, and Admin can view the revision history (all content snapshots with author and timestamp) and workflow event history (all status transitions with actor, action, from/to status, note, timestamp).

**Why this priority**: Auditability and transparency are explicit requirements.

**Independent Test**: Can be tested by viewing history tabs for any article across roles.

**Acceptance Scenarios**:

1. **Given** article with multiple revisions, **When** authorized user views history, **Then** all revisions listed with revision number, editor, timestamp, content preview
2. **Given** article with workflow events, **When** authorized user views workflow history, **Then** all events listed chronologically with actor, action, from/to status, note, timestamp
3. **Given** Author views their article history, **Then** they see full revision and workflow history
4. **Given** unauthorized user attempts to view history, **When** request made, **Then** access denied

---

### Edge Cases

- What happens when an article is edited while in IN_EDITORIAL_REVIEW or PENDING_ADMIN_APPROVAL? → Status reverts to DRAFT or CHANGES_REQUESTED; prior approvals invalidated; must be resubmitted.
- How does system handle concurrent edits by Author and Editor? → Last save wins but creates new revision; prior approval invalidated per revision-binding rule.
- What happens when slug conflicts with existing published article? → Validation error on save; user can choose different slug.
- How are Markdown sanitization failures handled? → Sanitizer removes unsafe elements; safe HTML rendered; no error to user unless content becomes empty.
- What happens when bootstrap Admin credentials are missing on first run? → Application starts but logs warning; Admin must be created manually or via env on next restart.
- How does system handle deleted users? → Users are deactivated (soft delete) not hard-deleted; article history preserved with reference to deactivated user.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide user authentication with username/password; no public registration.
- **FR-002**: System MUST bootstrap an initial Admin user from environment variables on first run if no Admin exists.
- **FR-003**: System MUST enforce role-based access control server-side for all protected operations (not just UI hiding).
- **FR-004**: System MUST support four roles: Anonymous Visitor, Author, Editor, Admin with permissions per PRD-01 Section 5.
- **FR-005**: System MUST prevent the last active Admin from being deactivated or demoted.
- **FR-006**: System MUST store passwords using a secure standard algorithm (e.g., BCrypt); plaintext passwords never stored.
- **FR-007**: System MUST allow Authors to create, edit, and save article drafts (DRAFT status).
- **FR-008**: System MUST require title and body for articles; slug auto-generated if not provided but must be unique.
- **FR-009**: System MUST create a new ArticleRevision on every content change (title, excerpt, bodyMarkdown, tags); no revision on unchanged saves.
- **FR-010**: System MUST allow Authors to submit their DRAFT or CHANGES_REQUESTED articles for editorial review (→ IN_EDITORIAL_REVIEW).
- **FR-011**: System MUST provide Editors a queue of IN_EDITORIAL_REVIEW articles ordered by update time.
- **FR-012**: System MUST allow Editors to request changes with a mandatory note (→ CHANGES_REQUESTED).
- **FR-013**: System MUST allow Editors to approve editorial review (→ PENDING_ADMIN_APPROVAL).
- **FR-014**: System MUST allow Editors to edit article content during review; doing so creates new revision and reverts status to DRAFT.
- **FR-015**: System MUST provide Admins a list of PENDING_ADMIN_APPROVAL articles.
- **FR-016**: System MUST allow Admins to publish articles only when status is PENDING_ADMIN_APPROVAL AND current revision matches the reviewed revision.
- **FR-017**: System MUST allow Admins to reject with a mandatory note (→ CHANGES_REQUESTED).
- **FR-018**: System MUST allow Admins to unpublish PUBLISHED articles (→ DRAFT), immediately removing from public view.
- **FR-019**: System MUST record published_at timestamp only on successful publish; clear on unpublish.
- **FR-020**: System MUST maintain immutable ArticleRevision history for each article with revision number, content snapshot, editor, timestamp.
- **FR-021**: System MUST maintain append-only WorkflowEvent log for each article with actor, action, from/to status, note, timestamp, and linked revision.
- **FR-022**: System MUST bind editorial approval and admin publish decisions to the specific revision ID, not just article ID or status.
- **FR-023**: System MUST render Markdown to safe HTML on public pages; unsafe HTML/JS neutralized.
- **FR-024**: System MUST enforce unique slugs; reject duplicates with clear validation error.
- **FR-025**: System MUST return 404 for non-existent or non-published slugs without revealing draft existence.
- **FR-026**: System MUST provide RTL Persian UI for all pages; English and mixed content rendered correctly.
- **FR-027**: System MUST display validation and permission errors with user-friendly messages; no stack traces exposed.
- **FR-028**: System MUST run locally without external services, API keys, or internet for core workflow and tests.
- **FR-029**: System MUST support SQLite for local development and PostgreSQL for production via configuration.
- **FR-030**: System MUST use database migrations for schema management.

### Key Entities

- **User**: Represents a system account. Attributes: unique username, password hash, role (AUTHOR/EDITOR/ADMIN), active flag, creation timestamp. Soft-deleted (deactivated) to preserve history.
- **Article**: Represents a blog post. Attributes: author reference, status (DRAFT/IN_EDITORIAL_REVIEW/CHANGES_REQUESTED/PENDING_ADMIN_APPROVAL/PUBLISHED), current revision number, publication timestamp, creation/update timestamps.
- **ArticleRevision**: Immutable snapshot of article content at a point in time. Attributes: article reference, revision number, title, slug, excerpt, bodyMarkdown, tags, editor reference, creation timestamp.
- **WorkflowEvent**: Append-only record of a status transition. Attributes: article reference, optional revision reference, actor reference, action enum, from-status, to-status, optional note, timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Anonymous visitor can view published article list and detail pages with correct content in under 2 seconds on local hardware.
- **SC-002**: Author can create a draft, edit it 3 times, and submit for review — all revision history preserved and viewable.
- **SC-003**: Editor can request changes (with note) or approve; workflow events logged correctly for each action.
- **SC-004**: Admin can publish only when revision matches; attempt to publish stale revision is rejected with clear error.
- **SC-005**: Admin unpublish removes article from public pages immediately; article returns to DRAFT requiring full re-review.
- **SC-006**: Unauthorized access attempts (Author accessing other's draft, Editor publishing, visitor accessing admin) are denied server-side with appropriate HTTP status.
- **SC-007**: All 11 mandatory automated tests (per PRD-01 Section 11) pass in isolated local environment without network.
- **SC-008**: Bootstrap Admin created on first run; no duplicate on subsequent runs.
- **SC-009**: Markdown with `<script>alert(1)</script>` renders as safe text, not executable JavaScript.
- **SC-010**: Duplicate slug submission rejected with user-friendly error; form data retained.
- **SC-011**: Last active Admin cannot be deactivated or demoted via UI or API.

## Assumptions

- Target users are Persian-speaking content teams; UI is RTL Persian by default with English content support.
- Local development uses SQLite; production uses PostgreSQL — both via Django ORM migrations.
- No AI features in this phase (PRD-02/03); architecture must allow adding AI later without core rewrite.
- No concurrent editing UI (optimistic locking via revision binding is sufficient).
- No scheduling, comments, likes, newsletters, media uploads, or multi-blog support in this phase.
- Password reset via email is out of scope; Admin can reset by creating new user or direct DB update in dev.
- Deployment target is a single modular monolith application; no microservices, message queues, or Docker required for MVP.
- Django 5.2 LTS with Django Templates for server-rendered UI; no separate frontend framework.
- Ruff for linting/formatting; pytest for testing; python-dotenv for environment configuration.