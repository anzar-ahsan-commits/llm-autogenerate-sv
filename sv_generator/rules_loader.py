from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_rules(rules_path: Path) -> dict[str, Any]:
    content = rules_path.read_text(encoding='utf-8')
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        raise ValueError('Rules document must be a YAML mapping.')
    return document
