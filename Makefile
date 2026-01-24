.PHONY: all

local-run-dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

local-run-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build