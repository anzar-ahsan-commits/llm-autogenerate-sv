import json
from pathlib import Path

from sv_generator.generator import build_wiremock_mapping, generate_wiremock_assets
from sv_generator.postman import build_postman_collection


def test_build_wiremock_mapping() -> None:
    scenario = {
        'id': 'active-member',
        'name': 'Active member',
        'method': 'GET',
        'path': '/api/v1/eligibility/M1001',
        'expectedStatus': 200,
        'response': {'memberId': 'M1001', 'coverageStatus': 'ACTIVE', 'message': 'Member has active coverage.'},
    }
    mapping = build_wiremock_mapping(scenario)
    assert mapping['request']['method'] == 'GET'
    assert mapping['request']['urlPath'] == '/api/v1/eligibility/M1001'
    assert mapping['response']['status'] == 200
    assert mapping['response']['jsonBody']['coverageStatus'] == 'ACTIVE'


def test_generate_wiremock_assets(tmp_path: Path) -> None:
    scenarios = [
        {
            'id': 'active-member',
            'name': 'Active member',
            'method': 'GET',
            'path': '/api/v1/eligibility/M1001',
            'expectedStatus': 200,
            'response': {'memberId': 'M1001', 'coverageStatus': 'ACTIVE', 'message': 'Member has active coverage.'},
        }
    ]
    generate_wiremock_assets(scenarios, tmp_path)
    assert (tmp_path / 'wiremock' / 'mappings' / '01-active-member.json').exists()
    assert (tmp_path / 'wiremock' / '__files' / '01-active-member-response.json').exists()


def test_build_postman_collection_contains_items() -> None:
    scenarios = [
        {
            'id': 'active-member',
            'name': 'Active member',
            'method': 'GET',
            'path': '/api/v1/eligibility/M1001',
            'expectedStatus': 200,
            'response': {'memberId': 'M1001', 'coverageStatus': 'ACTIVE', 'message': 'Member has active coverage.'},
        }
    ]
    collection = build_postman_collection(scenarios)
    assert collection['item'][0]['name'] == 'Active member'
    assert collection['item'][0]['request']['url']['raw'] == 'http://localhost:8089/api/v1/eligibility/M1001'
