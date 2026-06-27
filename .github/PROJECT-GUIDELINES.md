# Project Guidelines

These core principles guide the design and evolution of llm-autogenerate-sv:

- **Synthetic healthcare data only** — Do not generate PHI, PII, real member data, or real patient information.
- **OpenAPI as contract** — The OpenAPI specification is the authoritative source for API structure, paths, methods, and response codes.
- **Scenario matrix as behavior** — The scenario matrix is the authoritative source for mock behavior and test coverage.
- **Derived artifacts** — Generated WireMock mappings, Postman collections, reports, and docs are derived from the source inputs, not authoritative themselves.
- **Simple and modular** — Keep code clean, testable, and easy to extend.
- **Deterministic output** — Prefer stable JSON output with consistent ordering for reproducible builds.
- **Documentation-first** — Update README.md and docs whenever behavior or command flow changes.

These guidelines ensure the project remains maintainable, auditable, and suitable for enterprise API governance workflows.
