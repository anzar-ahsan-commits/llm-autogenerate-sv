from pathlib import Path

from sv_generator.server import find_matching_mapping, load_wiremock_mappings


def test_load_wiremock_mappings(tmp_path: Path) -> None:
    mapping = {
        'request': {'method': 'GET', 'urlPath': '/api/v1/eligibility/M1001'},
        'response': {'status': 200, 'headers': {'Content-Type': 'application/json'}, 'jsonBody': {'memberId': 'M1001'}},
    }
    mapping_path = tmp_path / '01-active-member.json'
    mapping_path.write_text(
        '{"request": {"method": "GET", "urlPath": "/api/v1/eligibility/M1001"}, "response": {"status": 200, "headers": {"Content-Type": "application/json"}, "jsonBody": {"memberId": "M1001"}}}',
        encoding='utf-8',
    )
    mappings = load_wiremock_mappings(tmp_path)
    assert len(mappings) == 1
    assert mappings[0]['request']['urlPath'] == '/api/v1/eligibility/M1001'


def test_find_matching_mapping() -> None:
    mappings = [
        {'request': {'method': 'GET', 'urlPath': '/api/v1/eligibility/M1001'}, 'response': {'status': 200}},
        {'request': {'method': 'GET', 'urlPath': '/api/v1/eligibility/M1002'}, 'response': {'status': 200}},
    ]
    mapping = find_matching_mapping(mappings, 'GET', '/api/v1/eligibility/M1002')
    assert mapping is not None
    assert mapping['request']['urlPath'] == '/api/v1/eligibility/M1002'
