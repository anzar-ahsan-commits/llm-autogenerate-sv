import http.client
import json
import threading
from pathlib import Path

from sv_generator.mcp_server import MCPRequestHandler, ThreadedTCPServer


def start_test_server() -> tuple[ThreadedTCPServer, threading.Thread]:
    server = ThreadedTCPServer(('127.0.0.1', 0), MCPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_mcp_health_endpoint() -> None:
    server, thread = start_test_server()
    port = server.server_address[1]
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
    conn.request('GET', '/health')
    response = conn.getresponse()
    body = json.loads(response.read().decode('utf-8'))

    assert response.status == 200
    assert body['status'] == 'ok'

    server.shutdown()
    thread.join(timeout=1)


def test_mcp_generate_endpoint(tmp_path: Path) -> None:
    server, thread = start_test_server()
    port = server.server_address[1]
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=30)

    payload = {
        'openapi_path': 'input/openapi/eligibility-api-v1.yaml',
        'scenario_path': 'input/scenarios/eligibility-scenarios.yaml',
        'rules_path': 'input/test-data-rules/eligibility-data-rules.yaml',
        'output_root': str(tmp_path / 'generated'),
    }
    conn.request(
        'POST',
        '/generate',
        body=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
    )
    response = conn.getresponse()
    body = json.loads(response.read().decode('utf-8'))

    assert response.status == 200
    assert body['status'] == 'generated'
    assert Path(body['output_root']).exists()
    assert (Path(body['output_root']) / 'wiremock' / 'mappings').exists()

    server.shutdown()
    thread.join(timeout=1)
