#!/usr/bin/env sh
set -e

docker-compose up -d
printf 'Waiting for WireMock to become available...'
count=0
while ! curl -s http://localhost:8089/__admin/mappings > /dev/null 2>&1; do
  printf '.'
  sleep 1
  count=$((count + 1))
  if [ "$count" -ge 30 ]; then
    printf '\nWireMock did not become ready in time.\n'
    exit 1
  fi
done
printf '\nWireMock is ready at http://localhost:8089\n'
