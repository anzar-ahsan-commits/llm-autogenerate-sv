#!/usr/bin/env sh
set -e

if [ "$#" -eq 0 ]; then
  echo 'Usage: ./scripts/run-local-mock.sh generated/wiremock/mappings'
  exit 1
fi

mappings_dir="$1"
python3 -m sv_generator.cli serve --mappings "$mappings_dir" --host 127.0.0.1 --port 8089
