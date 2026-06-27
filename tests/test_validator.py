from sv_generator.scenario_loader import load_scenarios
from sv_generator.validator import validate_project


def test_validate_project_reports_error_for_missing_path_template(tmp_path) -> None:
    openapi = {'paths': {'/api/v1/eligibility/{memberId}': {'get': {'responses': {'200': {}}}}}}
    yaml_file = tmp_path / 'scenarios.yaml'
    yaml_file.write_text("""scenarios:
  - id: invalid-path
    name: Invalid path
    method: GET
    path: /api/v1/eligibility
    expectedStatus: 200
    response:
      memberId: M1001
      coverageStatus: ACTIVE
      message: Member has active coverage.
""", encoding='utf-8')
    scenarios = load_scenarios(yaml_file)
    report = validate_project(openapi=openapi, scenarios=scenarios, rules={})
    assert report.scenario_results[0].status == 'invalid'
    assert any('No OpenAPI path template matches' in error for error in report.scenario_results[0].errors)


def test_validate_project_reports_warning_for_unknown_error_code(tmp_path) -> None:
    openapi = {'paths': {'/api/v1/eligibility/{memberId}': {'get': {'responses': {'400': {}, '200': {}}}}}}
    yaml_file = tmp_path / 'scenarios.yaml'
    yaml_file.write_text("""scenarios:
  - id: bad-request
    name: Bad request
    method: GET
    path: /api/v1/eligibility/INVALID
    expectedStatus: 400
    response:
      errorCode: UNKNOWN
      message: Request failed due to malformed memberId.
""", encoding='utf-8')
    scenarios = load_scenarios(yaml_file)
    rules = {'errorCodes': {'BAD_REQUEST': {'status': 400}}}
    report = validate_project(openapi=openapi, scenarios=scenarios, rules=rules)
    assert report.scenario_results[0].warnings
    assert any('UNKNOWN' in warning for warning in report.scenario_results[0].warnings)
