from __future__ import annotations

from pathlib import Path
from typing import Any


def write_validation_report(report: Any, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'validation-report.md'
    lines: list[str] = []
    lines.append('# Validation Report')
    lines.append('')
    lines.append('## Summary')
    lines.append('')
    lines.append(f'- Total scenarios processed: {report.total_scenarios}')
    lines.append(f'- Mappings generated: {report.mappings_generated}')
    lines.append(f'- Errors: {len(report.errors)}')
    lines.append(f'- Warnings: {len(report.warnings)}')
    lines.append('')
    lines.append('## Source of truth')
    lines.append('')
    lines.append('The OpenAPI specification is the source of truth for API structure and supported HTTP methods/status codes. The scenario matrix is the source of truth for expected mock behavior and response payloads. Generated WireMock mappings, Postman collections, reports, and documentation are derived artifacts.')
    lines.append('')

    if report.errors:
        lines.append('## Errors')
        lines.append('')
        for error in report.errors:
            lines.append(f'- {error}')
        lines.append('')

    if report.warnings:
        lines.append('## Warnings')
        lines.append('')
        for warning in report.warnings:
            lines.append(f'- {warning}')
        lines.append('')

    lines.append('## Scenario results')
    lines.append('')
    for scenario_result in report.scenario_results:
        lines.append(f'### {scenario_result.name} (`{scenario_result.id}`)')
        lines.append('')
        lines.append(f'- path: `{scenario_result.path}`')
        lines.append(f'- validation status: **{scenario_result.status}**')
        if scenario_result.errors:
            lines.append('- errors:')
            for error in scenario_result.errors:
                lines.append(f'  - {error}')
        if scenario_result.warnings:
            lines.append('- warnings:')
            for warning in scenario_result.warnings:
                lines.append(f'  - {warning}')
        lines.append('')

    report_path.write_text('\n'.join(lines), encoding='utf-8')
