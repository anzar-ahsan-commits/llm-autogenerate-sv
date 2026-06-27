from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_openapi(openapi_path: Path) -> dict[str, Any]:
    content = openapi_path.read_text(encoding='utf-8')
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        raise ValueError('OpenAPI document must be a YAML mapping.')
    if 'paths' not in document:
        raise ValueError('OpenAPI document must contain a top-level paths section.')
    return document
