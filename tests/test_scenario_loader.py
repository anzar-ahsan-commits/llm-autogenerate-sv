from pathlib import Path

from sv_generator.scenario_loader import load_scenarios


def test_load_scenarios_success(tmp_path: Path) -> None:
    yaml_text = """scenarios:
  - id: active-member
    name: Active member
    method: GET
    path: /api/v1/eligibility/M1001
    expectedStatus: 200
    response:
      memberId: M1001
"""
    yaml_file = tmp_path / 'scenarios.yaml'
    yaml_file.write_text(yaml_text, encoding='utf-8')
    scenarios = load_scenarios(yaml_file)
    assert len(scenarios) == 1
    assert scenarios[0]['id'] == 'active-member'


def test_load_scenarios_invalid_document(tmp_path: Path) -> None:
    yaml_file = tmp_path / 'broken.yaml'
    yaml_file.write_text("""- not a mapping
""", encoding='utf-8')
    try:
        load_scenarios(yaml_file)
        assert False, 'Expected ValueError for invalid scenario document'
    except ValueError as exc:
        assert 'Scenario document' in str(exc)
