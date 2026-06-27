"""
Service Virtualization generator for synthesizing WireMock assets.

This package converts an approved OpenAPI contract, scenario matrix, and test data rules
into reproducible WireMock mappings, Postman collections, and validation reports.

Created by Anzar Ahsan.
"""

__all__ = [
    'cli',
    'core',
    'openapi_loader',
    'scenario_loader',
    'rules_loader',
    'validator',
    'generator',
    'postman',
    'report',
    'docs',
]
