PYTHON=python3

.PHONY: install generate start stop test smoke clean

install:
	$(PYTHON) -m pip install -r requirements.txt

generate:
	$(PYTHON) -m sv_generator.cli generate \
	  --openapi input/openapi/eligibility-api-v1.yaml \
	  --scenarios input/scenarios/eligibility-scenarios.yaml \
	  --rules input/test-data-rules/eligibility-data-rules.yaml \
	  --output generated

serve:
	./scripts/run-local-mock.sh generated/wiremock/mappings

start:
	docker-compose up -d

stop:
	docker-compose down

test:
	$(PYTHON) -m pytest

smoke:
	$(PYTHON) -m pytest -m smoke

clean:
	rm -rf generated/__pycache__ generated/wiremock/* generated/postman/* generated/reports/* generated/docs/*
