# PRD Versions — v1.0

| PRD | File | Size | Status |
|-----|------|------|--------|
| PRD-01 | `prd-01/PRD.md` | 20.6 KB | **Active** — Core Blog & Workflow |
| PRD-02 | `prd-02/PRD.md` | 18.6 KB | Pending — AI Writing & Editorial Tools |
| PRD-03 | `prd-03/PRD.md` | 17.7 KB | Pending — AI Blog Assistant |

## Version History

- **v1.0** (2026-10-19): Initial versioning of all 3 PRDs from `blog_prd_bundle/`

## Execution Order

1. **PRD-01** — Core Blog, Roles & Content Workflow (prerequisite for PRD-02/03)
2. PRD-02 — AI Writing & Editorial Tools (requires PRD-01 complete)
3. PRD-03 — AI Blog Assistant (requires PRD-01 complete)

## Tech Stack (from PRD-01)

- Java 17+, Spring Boot 3.x, Maven
- Spring MVC + Thymeleaf (server-rendered UI)
- Spring Security (auth + authorization)
- Spring Data JPA
- H2 (local/dev), PostgreSQL (production profile)
- JUnit 5 + Spring Boot Test
- Modular monolith (no microservices)
- Markdown → sanitized HTML