import requests

import pytest

BASE_URL = 'http://localhost:8089'


@pytest.mark.smoke
@pytest.mark.parametrize(
    'path,status,coverage',
    [
        ('/api/v1/eligibility/M1001', 200, 'ACTIVE'),
        ('/api/v1/eligibility/M1002', 200, 'INACTIVE'),
        ('/api/v1/eligibility/M9999', 404, None),
        ('/api/v1/eligibility/M5000', 503, None),
        ('/api/v1/eligibility/INVALID', 400, None),
    ],
)
def test_wiremock_scenarios(path: str, status: int, coverage: str | None) -> None:
    response = requests.get(f'{BASE_URL}{path}', timeout=5)
    assert response.status_code == status
    if coverage is not None:
        body = response.json()
        assert body['coverageStatus'] == coverage
