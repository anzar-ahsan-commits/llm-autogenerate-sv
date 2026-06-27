"""
Local Python-based mock server for serving WireMock mappings.

Provides a pure-Python HTTP mock runtime as an alternative to Docker + WireMock,
useful for development and lightweight testing scenarios.

Supports basic request matching (method, path), response status codes, headers,
JSON bodies, and fixed delays.
"""

from __future__ import annotations

import argparse
import http.server
import json
import socketserver
import time
import urllib.parse
from pathlib import Path
from typing import Any


def load_wiremock_mappings(mappings_root: Path) -> list[dict[str, Any]]:
    if not mappings_root.exists() or not mappings_root.is_dir():
        raise FileNotFoundError(f'WireMock mappings directory not found: {mappings_root}')

    mappings: list[dict[str, Any]] = []
    for mapping_file in sorted(mappings_root.glob('*.json')):
        content = mapping_file.read_text(encoding='utf-8')
        mapping = json.loads(content)
        if not isinstance(mapping, dict):
            raise ValueError(f'Mapping file must contain a JSON object: {mapping_file}')
        mappings.append(mapping)
    return mappings


def find_matching_mapping(mappings: list[dict[str, Any]], method: str, path: str) -> dict[str, Any] | None:
    for mapping in mappings:
        request = mapping.get('request', {})
        if request.get('method') != method:
            continue
        if request.get('urlPath') != path:
            continue
        return mapping
    return None


class WireMockRequestHandler(http.server.BaseHTTPRequestHandler):
    mappings: list[dict[str, Any]] = []

    def do_GET(self) -> None:
        self.handle_mock_request()

    def do_POST(self) -> None:
        self.handle_mock_request()

    def do_PUT(self) -> None:
        self.handle_mock_request()

    def do_DELETE(self) -> None:
        self.handle_mock_request()

    def handle_mock_request(self) -> None:
        method = self.command
        url = urllib.parse.urlparse(self.path)
        mapping = find_matching_mapping(self.mappings, method, url.path)
        if mapping is None:
            self.send_error(404, 'No matching mapping found')
            return

        response = mapping.get('response', {})
        delay = response.get('fixedDelayMilliseconds')
        if isinstance(delay, int) and delay > 0:
            time.sleep(delay / 1000.0)

        body = response.get('jsonBody', {})
        response_body = json.dumps(body, indent=2).encode('utf-8')

        status = response.get('status', 200)
        self.send_response(status)
        headers = response.get('headers', {})
        for name, value in headers.items():
            self.send_header(name, str(value))
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format: str, *args: Any) -> None:
        # suppress default logging to keep output clean
        return


def run_server(mappings_root: Path, host: str = '0.0.0.0', port: int = 8089) -> None:
    mappings = load_wiremock_mappings(mappings_root)
    handler = WireMockRequestHandler
    handler.mappings = mappings

    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadedTCPServer((host, port), handler) as server:
        print(f'Starting local mock server at http://{host}:{port}')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Local mock server stopped.')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Serve generated mappings with a local Python mock server.')
    parser.add_argument('--mappings', required=True, help='Path to generated WireMock mapping JSON files.')
    parser.add_argument('--host', default='0.0.0.0', help='Host for the local server.')
    parser.add_argument('--port', type=int, default=8089, help='Port for the local server.')
    args = parser.parse_args(argv)

    run_server(Path(args.mappings).expanduser(), host=args.host, port=args.port)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
