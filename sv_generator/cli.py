"""
Command-line interface for the Service Virtualization generator.

Usage:
  python -m sv_generator.cli generate --openapi ... --scenarios ... --rules ... --output ...
  python -m sv_generator.cli serve --mappings ... --host ... --port ...
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .core import generate_artifacts
from .server import run_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Generate Service Virtualization assets from OpenAPI, scenarios, and rules.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    generate_parser = subparsers.add_parser('generate', help='Generate WireMock mappings and supporting assets.')
    generate_parser.add_argument('--openapi', required=True, help='Path to the OpenAPI YAML file.')
    generate_parser.add_argument('--scenarios', required=True, help='Path to the scenario matrix YAML file.')
    generate_parser.add_argument('--rules', required=True, help='Path to the synthetic test data rules YAML file.')
    generate_parser.add_argument('--output', required=True, help='Output root folder for generated assets.')

    serve_parser = subparsers.add_parser('serve', help='Run a local Python mock server from generated mappings.')
    serve_parser.add_argument('--mappings', required=True, help='Path to generated WireMock mapping JSON files.')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host for the local mock server.')
    serve_parser.add_argument('--port', type=int, default=8089, help='Port for the local mock server.')

    args = parser.parse_args(argv)
    if args.command == 'generate':
        try:
            generate_artifacts(
                openapi_path=Path(args.openapi),
                scenario_path=Path(args.scenarios),
                rules_path=Path(args.rules),
                output_root=Path(args.output),
            )
            return 0
        except Exception as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 1

    if args.command == 'serve':
        try:
            run_server(
                mappings_root=Path(args.mappings),
                host=args.host,
                port=args.port,
            )
            return 0
        except Exception as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 1

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
