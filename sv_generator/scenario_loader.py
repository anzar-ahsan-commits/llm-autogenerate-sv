from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_scenarios(scenario_path: Path) -> list[dict[str, Any]]:
    content = scenario_path.read_text(encoding='utf-8')
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        raise ValueError('Scenario document must be a YAML mapping.')
    scenarios = document.get('scenarios')
    if not isinstance(scenarios, list):
        raise ValueError('Scenario document must contain a list under the key "scenarios".')
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError('Each scenario entry must be a mapping.')
    return scenarios
