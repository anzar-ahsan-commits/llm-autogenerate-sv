# Contributing to llm-autogenerate-sv

Thank you for your interest in this Service Virtualization reference implementation.

This is a human-built engineering project created by **Anzar Ahsan** to demonstrate professional API governance and mock service automation practices. Contributions are welcome and should maintain the project's focus on clarity, maintainability, and audit-friendly design.

## Goals

This repository is intended to be:

- Clear and straightforward to understand
- Driven by authoritative source inputs (OpenAPI, scenario matrix)
- Deterministic and fully reproducible
- Suitable for GitHub sharing and portfolio discussions
- Valuable as a reference for regulated API environments

## How to contribute

1. Fork the repository.
2. Create a feature branch with a descriptive name.
3. Run the tests and verify the project still works:

```bash
make install
make test
```

4. Open a pull request with a clear summary of the proposed change.

## Development workflow

- Use the approved OpenAPI spec as the source of truth for API behaviors.
- Use the scenario matrix as the source of truth for mock cases.
- Keep generated files out of source control by using `.gitignore`.
- Keep code modular and easy to maintain.

## Local environment

```bash
python3 -m pip install -r requirements.txt
```

## Running the generator

```bash
make generate
```

## Starting the local mock server

```bash
./scripts/run-local-mock.sh generated/wiremock/mappings
```

## Starting the MCP integration server

```bash
./scripts/run-mcp.sh
```

## Running smoke tests

```bash
make smoke
```

## Notes

- Use synthetic healthcare data only.
- Do not add PHI, PII, or real member information.
- Do not embed proprietary or customer-specific data.
