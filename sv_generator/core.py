from __future__ import annotations

from pathlib import Path

from .openapi_loader import load_openapi
from .scenario_loader import load_scenarios
from .rules_loader import load_rules
from .validator import validate_project
from .generator import generate_wiremock_assets
from .postman import generate_postman_collection
from .report import write_validation_report
from .docs import write_documentation


def generate_artifacts(
    openapi_path: Path,
    scenario_path: Path,
    rules_path: Path,
    output_root: Path,
) -> None:
    openapi_path = openapi_path.expanduser()
    scenario_path = scenario_path.expanduser()
    rules_path = rules_path.expanduser()
    output_root = output_root.expanduser()

    output_root.mkdir(parents=True, exist_ok=True)

    openapi = load_openapi(openapi_path)
    scenarios = load_scenarios(scenario_path)
    rules = load_rules(rules_path)

    report = validate_project(openapi=openapi, scenarios=scenarios, rules=rules)
    report.mappings_generated = len(scenarios)

    reports_dir = output_root / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    write_validation_report(report=report, output_dir=reports_dir)

    if report.errors:
        raise RuntimeError('Validation failed. See generated/reports/validation-report.md for details.')

    generate_wiremock_assets(scenarios=scenarios, output_root=output_root)
    generate_postman_collection(scenarios=scenarios, output_root=output_root)
    write_documentation(openapi=openapi, scenarios=scenarios, output_root=output_root)
