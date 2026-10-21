# Contracts Directory

**Feature**: 001-core-blog-workflow
**Status**: Empty — No External Interfaces

## Reason

This phase (PRD-01) implements a **server-rendered Django web application** using Django Templates. There are no:

- REST APIs
- GraphQL endpoints
- gRPC services
- CLI commands (beyond Django management commands)
- Message queues
- WebSocket interfaces
- External system integrations

All user interactions occur through HTML forms and links rendered by Django views. Internal contracts (view function signatures, form classes, model methods, template contexts) are documented in code via:

- Type hints (PEP 484)
- Docstrings (Google/NumPy style)
- Django form/widget validation
- Template context documentation

## Future Contracts (PRD-02/03)

When AI features are added in later phases, this directory will contain:

| Phase | Contract Type | Description |
|-------|---------------|-------------|
| PRD-02 | AI Provider Interface | `AIProvider` protocol for generation/review |
| PRD-02 | Prompt Templates | Versioned prompt files for each AI task |
| PRD-02 | Output Schemas | Pydantic models for AI response validation |
| PRD-03 | Assistant Query API | Internal endpoint for RAG queries |
| PRD-03 | Search/Retrieval Contract | Vector search interface |

---

**Generated**: 2026-10-19 by `/speckit.plan`
**Location**: `specs/001-core-blog-workflow/contracts/`