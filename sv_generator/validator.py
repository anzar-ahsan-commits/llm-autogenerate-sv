from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScenarioValidationResult:
    id: str
    name: str
    path: str
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    total_scenarios: int = 0
    mappings_generated: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scenario_results: list[ScenarioValidationResult] = field(default_factory=list)


def validate_project(openapi: dict[str, Any], scenarios: list[dict[str, Any]], rules: dict[str, Any]) -> ValidationReport:
    report = ValidationReport(total_scenarios=len(scenarios))
    if not isinstance(openapi, dict):
        report.errors.append('OpenAPI payload is not a mapping.')
        return report
    if 'paths' not in openapi or not isinstance(openapi['paths'], dict):
        report.errors.append('OpenAPI payload must contain top-level paths mapping.')
        return report

    for scenario in scenarios:
        scenario_result = validate_scenario(openapi, scenario, rules)
        report.scenario_results.append(scenario_result)
        report.errors.extend(scenario_result.errors)
        report.warnings.extend(scenario_result.warnings)

    if not scenarios:
        report.warnings.append('No scenarios were found in the scenario matrix.')

    return report


def validate_scenario(openapi: dict[str, Any], scenario: dict[str, Any], rules: dict[str, Any]) -> ScenarioValidationResult:
    scenario_id = str(scenario.get('id', 'unknown'))
    scenario_name = str(scenario.get('name', 'unnamed scenario'))
    scenario_path = str(scenario.get('path', ''))
    result = ScenarioValidationResult(
        id=scenario_id,
        name=scenario_name,
        path=scenario_path,
        status='pending',
    )

    required_fields = ['id', 'name', 'method', 'path', 'expectedStatus', 'response']
    for field_name in required_fields:
        if field_name not in scenario:
            result.errors.append(f'Missing required field: {field_name}')

    if result.errors:
        result.status = 'invalid'
        return result

    actual_method = str(scenario['method']).lower()
    openapi_paths = openapi.get('paths', {})
    matching_template = find_matching_path_template(list(openapi_paths.keys()), scenario_path)
    if matching_template is None:
        result.errors.append(f'No OpenAPI path template matches scenario path: {scenario_path}')
        result.status = 'invalid'
        return result

    operation = openapi_paths[matching_template].get(actual_method)
    if operation is None:
        result.errors.append(f'HTTP method {scenario["method"]} is not defined for OpenAPI path {matching_template}')
        result.status = 'invalid'
        return result

    responses = operation.get('responses', {})
    expected_status = validate_expected_status(scenario['expectedStatus'], result)
    if expected_status is not None and str(expected_status) not in responses:
        result.errors.append(
            f'Expected status {expected_status} is not defined in OpenAPI for {matching_template} {scenario["method"]}'
        )

    response_payload = scenario['response']
    try:
        json.dumps(response_payload)
    except (TypeError, ValueError) as exc:
        result.errors.append(f'Response payload is not JSON serializable: {exc}')

    if expected_status == 200:
        validate_payload_fields(response_payload, ['memberId', 'coverageStatus', 'message'], result)
    elif expected_status is not None:
        validate_payload_fields(response_payload, ['errorCode', 'message'], result)

    if rules:
        result.warnings.extend(validate_using_rules(response_payload, rules))

    result.warnings.extend(validate_path_parameters(matching_template, scenario_path, openapi_paths[matching_template], operation))
    result.warnings.extend(validate_fixed_delay(scenario, result))
    result.warnings.extend(detect_pii_in_payload(scenario))
    result.status = 'valid' if not result.errors else 'invalid'
    return result


def validate_expected_status(expected_status: Any, result: ScenarioValidationResult) -> int | None:
    if isinstance(expected_status, int):
        return expected_status
    if isinstance(expected_status, str) and expected_status.isdigit():
        return int(expected_status)
    result.errors.append('expectedStatus must be an integer or numeric string.')
    return None


def validate_payload_fields(payload: Any, required_fields: list[str], result: ScenarioValidationResult) -> None:
    if not isinstance(payload, dict):
        result.errors.append('Response payload must be a JSON object.')
        return
    for required in required_fields:
        if required not in payload:
            result.errors.append(f'Response payload missing required field: {required}')


def validate_path_parameters(
    template: str,
    scenario_path: str,
    path_item: dict[str, Any],
    operation: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    path_params = extract_path_parameters(template, scenario_path)
    definitions = collect_path_parameter_definitions(path_item, operation)

    for name, value in path_params.items():
        schema = definitions.get(name, {}).get('schema', {})
        if not isinstance(schema, dict):
            continue
        pattern = schema.get('pattern')
        if pattern and not re.fullmatch(pattern, value):
            warnings.append(
                f'Path parameter {name} value {value!r} does not match OpenAPI pattern {pattern!r}.'
            )
        enum_values = schema.get('enum')
        if isinstance(enum_values, list) and value not in enum_values:
            warnings.append(
                f'Path parameter {name} value {value!r} is not in allowed enum values {enum_values!r}.'
            )

    return warnings


def extract_path_parameters(template: str, scenario_path: str) -> dict[str, str]:
    template_parts = template.strip('/').split('/')
    path_parts = scenario_path.strip('/').split('/')
    values: dict[str, str] = {}
    for template_part, path_part in zip(template_parts, path_parts):
        if template_part.startswith('{') and template_part.endswith('}'):
            values[template_part[1:-1]] = path_part
    return values


def collect_path_parameter_definitions(path_item: dict[str, Any], operation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    parameters: dict[str, dict[str, Any]] = {}
    for source in (path_item.get('parameters', []), operation.get('parameters', [])):
        if not isinstance(source, list):
            continue
        for parameter in source:
            if isinstance(parameter, dict) and parameter.get('in') == 'path' and parameter.get('name'):
                parameters[parameter['name']] = parameter
    return parameters


def validate_fixed_delay(scenario: dict[str, Any], result: ScenarioValidationResult) -> list[str]:
    warnings: list[str] = []
    if 'fixedDelayMilliseconds' not in scenario:
        return warnings
    delay = scenario['fixedDelayMilliseconds']
    if not isinstance(delay, int) or delay < 0:
        result.errors.append('fixedDelayMilliseconds must be a non-negative integer.')
    return warnings


def find_matching_path_template(templates: list[str], scenario_path: str) -> str | None:
    for template in templates:
        regex = path_template_to_regex(template)
        if re.fullmatch(regex, scenario_path):
            return template
    return None


def path_template_to_regex(path_template: str) -> str:
    escaped = re.escape(path_template)
    pattern = re.sub(r'\\\{[^\\}]+\\\}', '[^/]+', escaped)
    return f'^{pattern}$'


def validate_using_rules(response_payload: Any, rules: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if not isinstance(response_payload, dict):
        return warnings

    allowed = rules.get('coverageStatus', {}).get('allowed')
    if isinstance(allowed, list) and 'coverageStatus' in response_payload:
        if response_payload['coverageStatus'] not in allowed:
            warnings.append(f"coverageStatus '{response_payload['coverageStatus']}' is not allowed by rules.")

    error_code = response_payload.get('errorCode')
    if error_code and 'errorCodes' in rules and error_code not in rules['errorCodes']:
        warnings.append(f"errorCode '{error_code}' is not defined in rules.")

    return warnings


def detect_pii_in_payload(item: Any) -> list[str]:
    warnings: list[str] = []
    if isinstance(item, dict):
        for value in item.values():
            warnings.extend(detect_pii_in_payload(value))
        return warnings
    if isinstance(item, list):
        for value in item:
            warnings.extend(detect_pii_in_payload(value))
        return warnings
    if isinstance(item, str):
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',
            r'\b\d{4} \d{4} \d{4} \d{4}\b',
            r'\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b',
            r'\b(?:ssn|social security|patient|mrn|dob)\b',
        ]
        for pattern in pii_patterns:
            if re.search(pattern, item, re.IGNORECASE):
                warnings.append(f'Possible PII/PHI detected in string: "{item}"')
    return warnings
