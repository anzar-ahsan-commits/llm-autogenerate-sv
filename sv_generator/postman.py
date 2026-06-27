from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_postman_collection(scenarios: list[dict[str, Any]], output_root: Path) -> None:
    postman_dir = output_root / 'postman'
    postman_dir.mkdir(parents=True, exist_ok=True)
    collection = build_postman_collection(scenarios)
    collection_path = postman_dir / 'eligibility-api.postman_collection.json'
    collection_path.write_text(json.dumps(collection, indent=2), encoding='utf-8')


def build_postman_collection(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    items = [build_postman_item(scenario) for scenario in scenarios]
    return {
        'info': {
            'name': 'Eligibility API mock scenarios',
            'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
            'version': '1.0.0',
        },
        'item': items,
    }


def build_postman_item(scenario: dict[str, Any]) -> dict[str, Any]:
    raw_url = f'http://localhost:8089{scenario["path"]}'
    return {
        'name': scenario['name'],
        'request': {
            'method': scenario['method'],
            'header': [{'key': 'Content-Type', 'value': 'application/json'}],
            'url': build_postman_url(raw_url),
        },
        'response': [],
    }


def build_postman_url(raw_url: str) -> dict[str, Any]:
    without_scheme = raw_url.replace('http://', '')
    parts = without_scheme.split('/')
    host_port = parts[0] if parts else 'localhost:8089'
    host, _, port = host_port.partition(':')
    if not port:
        port = '8089'
    path = parts[1:]
    return {
        'raw': raw_url,
        'protocol': 'http',
        'host': [host],
        'port': port,
        'path': path,
    }
