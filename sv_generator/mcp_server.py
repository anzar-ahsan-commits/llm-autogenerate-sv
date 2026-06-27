from __future__ import annotations

import http.server
import json
import socketserver
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .core import generate_artifacts


def parse_json_body(request: http.server.BaseHTTPRequestHandler) -> dict[str, Any]:
    length_header = request.headers.get('Content-Length')
    if length_header is None:
        return {}
    raw_body = request.rfile.read(int(length_header))
    if not raw_body:
        return {}
    return json.loads(raw_body.decode('utf-8'))


def send_json_response(request: http.server.BaseHTTPRequestHandler, code: int, payload: dict[str, Any]) -> None:
    response_body = json.dumps(payload, indent=2).encode('utf-8')
    request.send_response(code)
    request.send_header('Content-Type', 'application/json; charset=utf-8')
    request.send_header('Content-Length', str(len(response_body)))
    request.end_headers()
    request.wfile.write(response_body)


class MCPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == '/health':
            send_json_response(self, 200, {'status': 'ok'})
            return

        if route == '/version':
            send_json_response(self, 200, {'version': '0.1.0'})
            return

        self.send_error(404, 'Endpoint not found')

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route == '/generate':
            self.handle_generate()
            return

        self.send_error(404, 'Endpoint not found')

    def handle_generate(self) -> None:
        try:
            payload = parse_json_body(self)
            openapi_path = Path(payload['openapi_path']).expanduser()
            scenario_path = Path(payload['scenario_path']).expanduser()
            rules_path = Path(payload['rules_path']).expanduser()
            output_root = Path(payload['output_root']).expanduser()

            generate_artifacts(
                openapi_path=openapi_path,
                scenario_path=scenario_path,
                rules_path=rules_path,
                output_root=output_root,
            )
            send_json_response(self, 200, {
                'status': 'generated',
                'output_root': str(output_root),
                'mappings_root': str(output_root / 'wiremock' / 'mappings'),
            })
        except Exception as exc:
            send_json_response(self, 500, {
                'status': 'error',
                'message': str(exc),
            })

    def log_message(self, format: str, *args: Any) -> None:
        return


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def run_mcp_server(host: str = '0.0.0.0', port: int = 9000) -> None:
    handler = MCPRequestHandler

    with ThreadedTCPServer((host, port), handler) as server:
        print(f'Starting MCP-ready integration server at http://{host}:{port}')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('MCP integration server stopped.')
