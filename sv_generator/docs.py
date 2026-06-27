from __future__ import annotations

from pathlib import Path
from typing import Any


def write_documentation(openapi: dict[str, Any], scenarios: list[dict[str, Any]], output_root: Path) -> None:
    docs_dir = output_root / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_path = docs_dir / 'README.md'
    lines: list[str] = []
    title = openapi.get('info', {}).get('title', 'Generated Service Virtualization Assets')
    version = openapi.get('info', {}).get('version', '1.0.0')
    description = openapi.get('info', {}).get('description', '')

    lines.append(f'# Generated documentation for {title}')
    lines.append('')
    lines.append(f'**Version:** {version}')
    lines.append('')
    if description:
        lines.append(description)
        lines.append('')
    lines.append('## Generated asset overview')
    lines.append('')
    lines.append('- `generated/wiremock/mappings/` — WireMock mapping JSON files per scenario')
    lines.append('- `generated/wiremock/__files/` — generated response body assets')
    lines.append('- `generated/postman/eligibility-api.postman_collection.json` — Postman collection for API scenarios')
    lines.append('- `generated/reports/validation-report.md` — validation status and notes')
    lines.append('')
    lines.append('## Scenario matrix')
    lines.append('')
    for scenario in scenarios:
        lines.append(f'- **{scenario["name"]}**: `{scenario["path"]}` → {scenario["expectedStatus"]}')
    lines.append('')
    doc_path.write_text('\n'.join(lines), encoding='utf-8')
