from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_wiremock_assets(scenarios: list[dict[str, Any]], output_root: Path) -> None:
    wiremock_root = output_root / 'wiremock'
    mappings_dir = wiremock_root / 'mappings'
    files_dir = wiremock_root / '__files'
    mappings_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(parents=True, exist_ok=True)

    for index, scenario in enumerate(scenarios, start=1):
        mapping = build_wiremock_mapping(scenario)
        mapping_path = mappings_dir / f'{index:02d}-{scenario["id"]}.json'
        mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding='utf-8')

        response_file = files_dir / f'{index:02d}-{scenario["id"]}-response.json'
        response_file.write_text(json.dumps(scenario['response'], indent=2, sort_keys=True), encoding='utf-8')

    files_readme = files_dir / 'README.md'
    files_readme.write_text(
        'This directory contains generated response bodies associated with WireMock mappings.',
        encoding='utf-8',
    )


def build_wiremock_mapping(scenario: dict[str, Any]) -> dict[str, Any]:
    request_payload = {
        'method': scenario['method'],
        'urlPath': scenario['path'],
    }
    response_payload: dict[str, Any] = {
        'status': scenario['expectedStatus'],
        'headers': {'Content-Type': 'application/json'},
        'jsonBody': scenario['response'],
    }
    if scenario.get('fixedDelayMilliseconds') is not None:
        response_payload['fixedDelayMilliseconds'] = scenario['fixedDelayMilliseconds']
    return {'request': request_payload, 'response': response_payload}
